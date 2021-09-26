
import pandas as pd

def class_signal_summary(y_test, preds):
    """Print a brief summary of a classification model's signal distribution.
    Returns a dataframe comparing predictions with test dependent variable and prints % of bullish and bearish signals."""

    df_tvp = pd.DataFrame({'Test Set':y_test, 'Predictions': preds})
    print(df_tvp['Predictions'].value_counts())
    bulls = float((df_tvp.loc[df_tvp['Predictions'] ==  1, ['Predictions']]).count() /  df_tvp['Predictions'].count())
    neuts = float((df_tvp.loc[df_tvp['Predictions'] ==  0, ['Predictions']]).count() /  df_tvp['Predictions'].count())
    bears = float((df_tvp.loc[df_tvp['Predictions'] ==  -1, ['Predictions']]).count() /  df_tvp['Predictions'].count())
    print (f"Bullish Signals: {bulls:,.2%}")
    print (f"Neutral Signals: {neuts:,.2%}")
    print (f"Barish Signals: {bears:,.2%}")

    return df_tvp