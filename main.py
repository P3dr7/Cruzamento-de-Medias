import pandas as pd

file_path = 'EURUSD_M5.csv'

columns_to_drop = ['<TICKVOL>', '<VOL>', '<SPREAD>']

def load_data(file_path):
    """
    Load the CSV file into a pandas DataFrame.
    """
    try:
        df = pd.read_csv(file_path, sep='\t')
        print(f"Data loaded successfully from {file_path}.")
        # print(df.head())
        for col in columns_to_drop:
            if col not in df.columns:
                print(
                    f"Aviso: A coluna '{col}' não foi encontrada no DataFrame. Verifique a ortografia e o delimitador.")
        df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

        df['<OPEN>'] = pd.to_numeric(df['<OPEN>'], errors='coerce')
        df['<CLOSE>'] = pd.to_numeric(df['<CLOSE>'], errors='coerce')
        df['<HIGH>'] = pd.to_numeric(df['<HIGH>'], errors='coerce')
        df['<LOW>'] = pd.to_numeric(df['<LOW>'], errors='coerce')
        # print(df.head())
        return df
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None


def calculate_moving_averages(df, windows):
    """
    Calculate moving averages for a list of window sizes.
    """
    if df is not None and '<CLOSE>' in df.columns:
        for window in windows:
            df[f'MA{window}'] = df['<CLOSE>'].rolling(window=window).mean()
        return df
    else:
        print("DataFrame is empty or 'Close' column is missing.")
        return None


def main():
    df = load_data(file_path)

    if df is not None:
        ma_windows = [20, 50, 200]
        df = calculate_moving_averages(df, ma_windows)

        if df is not None:
            print(df.tail())
        else:
            print("Failed to calculate moving averages.")
    else:
        print("Failed to load data.")


def posicao():
    """
    Placeholder for position management logic.
    """
    print("Position management logic goes here.")


if __name__ == "__main__":
    main()