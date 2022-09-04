# Decline-Curve-Analysis
### Decline curve analysis web application with streamlit:
- take the well or field data 
- specify the prameters [ data column , production column ]
- apply Arp's model on the data after smoothing with moving average 
-  Try the app [Streamlit_DCA_App](https://decline-curve-analysis.herokuapp.com/)
## dca python module and the ARPS class:
1. Create the ARP's object with its parameter

```python
arps_model = ARPS( producation_data , production_col , date_col )
"""
production_data : pandas.DataFrame  
production_col : str -> the name of oil or gas production column
date_col : str -> name of the date column ( data of production )
"""
```
2. Smooth the data
   - Smoothing the production data and remove the outliers
  ```python
  df_smoothed = arps_model.smooth(window_size : int , stds :int , trim : bool )
  """
    window_size : int -> the size of the window for the moving  average
    stds : int -> number of standard deviations to remove data  after [ for the outliers ]
    trim : bool -> whether to trim the data in which the production increase or not
    return :
        df : pd.DataFrame -> the data frame after smoothing and removing the outiler to show the data
  """
  ``` 
  3. Process the date_column 
      - the date_of production in the form of date like (1-4-2019) need to preprocced to int to be used in fitting 
  ```python
  arps_model.prepocess_date_col(frequency : str )
  """
    frequency : the frequency of the production data taken [ Daily , Monthly , Yearly ]
  """
  ```
  3. Fit the data and get the ARP's parameters
   -    you can fit each model separatly
  ```python 
  parameters , Q_fitted = arps_model.fit_exponential()
  parameters , Q_fitted = arps_model.fit_hyperbolic()
  parameters , Q_fitted = arps_model.fit_harmonic()

  """
    Fit the data only for the Exponential model
    return : parameters , values of the fitted line to draw
    ( prarameter -> [qi, di , b , RMSE , model_name ])
  """
  ```
  - or you can fit all the model at once
  ```python
   parameters , Qs_fitted = arps_model.fit_all_models()
   """
    return :
         data_parameters : Dict -> a dictionary of all the information and parameters of each model [ qi, di , b , rmse ]
         Qs : pandas.DataFrame -> dataframe for these columns [ Time, originalSmoothed_Q , Exponential_fitted_Q , Hyperbolic_fiited_Q , Harmonic_fitted_Q ] to draw and see the rasults.
   """
  ```

