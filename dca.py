from pandas import to_datetime
from scipy.optimize import curve_fit
import numpy as np
'-------------------- RSME ------------------'
def rmse(y, yfit):
      N = len(y)
      return np.sqrt(np.sum(y-yfit)**2 / N)
    
def hyperbolic(t, qi, di, b):
          return qi / (np.abs((1 + b * di * t))**(1/b))
        
def exposential(t,qi,di):
        return qi* np.exp(-di*t)
      
def harmonic(t,qi,di):
        return qi/(1+di*t)
'-------------------- HYPERPOLIC FIT ------------------'
def hyperbolic_fit(t,q):
      
      # fitting the data with the hyperbolic function
      t_normalized = t / max(t)
      q_normalized = q / max(q)  
      # t_test_normalized = t_test / max(t_test)
      # q_test_normalized = q_test / max(q_test) 
        # fitting the data with the hyperbolic function
      popt, pcov = curve_fit(hyperbolic, t_normalized, q_normalized)
      qi, di,b= popt

        # RMSE is calculated on the normalized variables
      qfit_normalized = hyperbolic(t_normalized, qi, di, b)
      RMSE = rmse(q_normalized, qfit_normalized)

        # De-normalize qi and di
      qi = qi * max(q)
      di = di / max(t)
      parameters = [qi,di,b,RMSE,"Hyperbolic"]
      return parameters
'-------------------- EXPONENTIAL FIT ------------------' 
def exponential_fit(t,q):
     
      # fitting the data with the hyperbolic function
      t_normalized = t / max(t)
      q_normalized = q / max(q)  
      # t_test_normalized = t_test / max(t_test)
      # q_test_normalized = q_test / max(q_test) 
        # fitting the data with the hyperbolic function
      popt, pcov = curve_fit(exposential, t_normalized, q_normalized)
      qi, di= popt

        # RMSE is calculated on the normalized variables
      qfit_test_normalized = exposential(t_normalized, qi, di)
      RMSE = rmse(q_normalized, qfit_test_normalized)

        # De-normalize qi and di
      qi = qi * max(q)
      di = di / max(t)
      parameters = [qi,di,0,RMSE,"Exponential"]
      return parameters
'-------------------- HARMONIC FIT ------------------'
def harmonic_fit(t,q):
   
      
      # fitting the data with the hyperbolic function
      t_normalized = t / max(t)
      q_normalized = q / max(q)  
      # t_test_normalized = t_test / max(t_test)
      # q_test_normalized = q_test / max(q_test) 
        # fitting the data with the hyperbolic function
      popt, pcov = curve_fit(harmonic, t_normalized, q_normalized)
      qi, di= popt

        # RMSE is calculated on the normalized variables
      qfit_test_normalized = harmonic(t_normalized, qi, di)
      RMSE = rmse(q_normalized, qfit_test_normalized)

        # De-normalize qi and di
      qi = qi * max(q)
      di = di / max(t)
      parameters = [qi,di,1,RMSE,"Harmonic"]
      return parameters 

'-------------------- REMOVE_OUTLIERS ------------------'

def remove_outlier(df, column_name, window, number_of_stdevs_away_from_mean, trim=False):
  """
  Removing outlier of production data and trim initial buildup

  INPUT:

  df: Production dataframe
  column_name: Column name of production rate
  window: Rolling average window
  number_of_stdevs_away_from_mean: Distance from standard dev. where outliers will be removed
  trim: Option to trim initial buildup (Because buildup is an outlier). 
        Default is False.

  OUTPUT:

  df: New dataframe where outliers have been removed 
  """
  df[column_name+'_rol_Av']=df[column_name].rolling(window=window, center=True).mean()
  df[column_name+'_rol_Std']=df[column_name].rolling(window=window, center=True).std()

  # Detect anomalies by determining how far away from the mean (in terms of standard deviation)
  df[column_name+'_is_Outlier']=(abs(df[column_name]-df[
                                column_name+'_rol_Av'])>(
                                number_of_stdevs_away_from_mean*df[
                                column_name+'_rol_Std']))
    
    # outlier and not-outlier will be recorded in the '_is_Outlier'
    # column as 'True' and 'False'. Now, outlier is removed, so column that
    # contains 'True' values are masked out
  result = df.drop(df[df[column_name+'_is_Outlier'] == True].index).reset_index(drop=True)

  # Remove rows where "_rol_Av" has NaNs
  result = result[result[column_name+'_rol_Av'].notna()]  

  if trim==True:
    # Trim initial buildup
    maxi = result[column_name+'_rol_Av'].max()
    maxi_index = (result[result[column_name+'_rol_Av']==maxi].index.values)[0]
    result = result.iloc[maxi_index:,:].reset_index(drop=True)

  return result  
def PREPROCESS_DATA(df,time_col,Q_col,frequency):
        df[time_col] = to_datetime(df[time_col])
        df["Time [{frequency}]"] = (df[time_col] - df[time_col].iloc[0])
        if frequency == "Daily":
            df["Time [{frequency}]"] = df["Time [{frequency}]"] / np.timedelta64(1, 'D')
            df["Time [{frequency}]"] = df["Time [{frequency}]"].astype(int)
        elif frequency == "Monthly":
            df["Time [{frequency}]"] = df["Time [{frequency}]"] / np.timedelta64(1, 'M')
            df["Time [{frequency}]"] = df["Time [{frequency}]"].astype(int)
        elif frequency == "Yearly":
            df["Time [{frequency}]"] = df["Time [{frequency}]"] / np.timedelta64(1, 'Y')
            df["Time [{frequency}]"] = df["Time [{frequency}]"].astype(int)
        return df["Time [{frequency}]"] , df[Q_col+'_rol_Av']