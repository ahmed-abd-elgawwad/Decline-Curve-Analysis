# only one class to deal with all methods
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
class SingleModel:
    def __init__(self,Q,T):
        self.Q =Q
        self.T =T
        self.q_max = max(Q)
        self.T_max = max(T)
    def normalize(self):
        # normalize the columns
        self.T = self.T / max(self.T)
        self.Q = self.Q / max(self.Q)
    def RMSE(self,y , y_fit ):
        N = len(y)
        return np.sqrt(np.sum(y - y_fit) ** 2 / N)
        # De-normalize qi and di
    def hyperbolic(self,t, qi, di, b):
            return qi / (np.abs((1 + b * di * t)) ** (1 / b))

    def exposential(self,t, qi, di):
        return qi * np.exp(-di * t)

    def harmonic(self,t, qi, di):
        return qi / (1 + di * t)
class Exponential(SingleModel):
    def __init__(self,Q,T):
        SingleModel.__init__(self,Q,T)
    def fit(self):
        #normalize the data
        self.normalize()
        popt, pcov = curve_fit(self.exposential, self.T, self.Q)
        qi, di = popt
        qfit_normalized = self.exposential(self.T, qi, di)
        q_fitted = qfit_normalized * self.q_max
        RMSE = self.RMSE(self.Q, qfit_normalized)
        # De-normalize qi and di
        qi = qi * self.q_max
        di = di / self.T_max
        parameters = [qi, di, 0, RMSE, "Exponential"]
        return parameters , q_fitted
class Hyperbolic(SingleModel):
    def __init__(self,Q,T):
        SingleModel.__init__(self,Q,T)
    def fit(self):
        #normalize the data
        self.normalize()
        popt, pcov = curve_fit(self.hyperbolic, self.T, self.Q)
        qi, di,b = popt
        qfit_normalized = self.hyperbolic(self.T, qi, di,b)
        q_fitted = qfit_normalized * self.q_max
        RMSE = self.RMSE(self.Q, qfit_normalized)
        # De-normalize qi and di
        qi = qi * self.q_max
        di = di / self.T_max
        parameters = [qi, di, b, RMSE, "Hyperbolic"]
        return parameters , q_fitted
class Harmonic(SingleModel):
    def __init__(self,Q,T):
        SingleModel.__init__(self,Q,T)
    def fit(self):
        #normalize the data
        self.normalize()
        popt, pcov = curve_fit(self.harmonic, self.T, self.Q)
        qi, di= popt
        qfit_normalized = self.harmonic(self.T, qi, di)
        q_fitted = qfit_normalized * self.q_max
        RMSE = self.RMSE(self.Q, qfit_normalized)
        # De-normalize qi and di
        qi = qi * self.q_max
        di = di / self.T_max
        parameters = [qi, di, 1, RMSE, "Harmonic"]
        return parameters , q_fitted

class ARPS:
    """
    Takes the productions and date columns and provide ARP's paramters for the 3 models
    """
    def __init__(self, dataframe : pd.DataFrame , production_col : str , date_column :str):
        self.q = production_col
        self.date = date_column
        self.df = dataframe[[date_column,production_col]]
        self.Q = 0
        self.T =0
        self.ex_params = None
        self.hp_params = None
        self.Hr_params = None
    def smooth(self, window_size : int , stds : int , trim : bool ):
        # smoothing using moving average
        self.df[self.q + '_rol_Av'] = self.df[self.q].rolling(window=window_size, center=True).mean()
        # identify the outliers and remove them
        self.df[self.q + '_rol_Std'] = self.df[self.q].rolling(window=window_size, center=True).std()
        self.df[self.q + '_is_Outlier'] = (abs(self.df[self.q] - self.df[self.q + '_rol_Av']) > ( stds * self.df[self.q+'_rol_Std']))
        result = self.df.drop(self.df[self.df[self.q + '_is_Outlier'] == True].index).reset_index(drop=True)
        # Remove rows where "_rol_Av" has NaNs
        result = result[result[self.q + '_rol_Av'].notna()]
        # remove the increasing part of the curve we only concern about the decline part
        if trim == True:
            # Trim initial buildup
            maxi = result[self.q + '_rol_Av'].max()
            maxi_index = (result[result[self.q + '_rol_Av'] == maxi].index.values)[0]
            result = result.iloc[maxi_index:, :].reset_index(drop=True)
        self.df = result
        return self.df

    def prepocess_date_col(self,frequency = "Daily"):
        self.df[self.date] = pd.to_datetime(self.df[self.date])
        self.df["Time [{frequency}]"] = (self.df[self.date] - self.df[self.date].iloc[0])
        if frequency == "Daily":
            self.df["Time [{frequency}]"] = self.df["Time [{frequency}]"] / np.timedelta64(1, 'D')
            self.df["Time [{frequency}]"] = self.df["Time [{frequency}]"].astype(int)
        elif frequency == "Monthly":
            self.df["Time [{frequency}]"] = self.df["Time [{frequency}]"] / np.timedelta64(1, 'M')
            self.df["Time [{frequency}]"] = self.df["Time [{frequency}]"].astype(int)
        elif frequency == "Yearly":
            self.df["Time [{frequency}]"] = self.df["Time [{frequency}]"] / np.timedelta64(1, 'Y')
            self.df["Time [{frequency}]"] = self.df["Time [{frequency}]"].astype(int)
        self.T = self.df["Time [{frequency}]"]
        self.Q = self.df[self.q + '_rol_Av']

    def fit_exponential(self):
         parameters , q_fitted = Exponential(self.Q, self.T).fit()
         self.ex_params = parameters
         return parameters , q_fitted

    def fit_hyperbolic(self):
        parameters, q_fitted = Hyperbolic(self.Q, self.T).fit()
        self.hp_params = parameters
        return parameters , q_fitted

    def fit_harmonic(self):
        parameters, q_fitted = Harmonic(self.Q, self.T).fit()
        self.Hr_params = parameters
        return parameters , q_fitted

    def fit_all_models(self):
        ex ,qex = self.fit_exponential()
        hp , qhp= self.fit_hyperbolic()
        hr , qhr = self.fit_harmonic()
        all_params = [ex, hp, hr]
        data_info = {
            "Model": [i[-1] for i in all_params],
            "Qi": [i[0] for i in all_params],
            "Di": [i[1] for i in all_params],
            "b": [i[2] for i in all_params],
            "Normalized RMSE": [i[3] for i in all_params],
        }
        Qs = pd.DataFrame({
            "Time": self.T,
            "Original_Smoothed": self.Q,
            "Exponential": qex,
            "Hyperbolic": qhp,
            "Harmonic": qhr
        })
        return data_info , Qs





