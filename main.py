import pandas as pd

file_path = 'EURUSD_M5.csv'

columns_to_drop = ['<TICKVOL>', '<VOL>', '<SPREAD>']

# Lista para armazenar as operações como dicionários
operations = []
# Lista para gerenciar a posição aberta
positions = []


def load_data(file_path):
    """
    Load the CSV file into a pandas DataFrame.
    """
    try:
        df = pd.read_csv(file_path, sep='\t')
        print(f"Data loaded successfully from {file_path}.")

        # Converte a coluna '<DATE>' para o tipo de dado datetime
        df['<DATE>'] = pd.to_datetime(df['<DATE>'])

        for col in columns_to_drop:
            if col not in df.columns:
                print(
                    f"Aviso: A coluna '{col}' não foi encontrada no DataFrame. Verifique a ortografia e o delimitador.")
        df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

        df['<OPEN>'] = pd.to_numeric(df['<OPEN>'], errors='coerce')
        df['<CLOSE>'] = pd.to_numeric(df['<CLOSE>'], errors='coerce')
        df['<HIGH>'] = pd.to_numeric(df['<HIGH>'], errors='coerce')
        df['<LOW>'] = pd.to_numeric(df['<LOW>'], errors='coerce')
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
            df = ATR(df)
            posicao(df)
            print("Moving averages calculated successfully.")
            print("Positions:", positions)
            print("Results:", operations)

        else:
            print("Failed to calculate moving averages.")
    else:
        print("Failed to load data.")


def posicao(df):
    """
    Placeholder for position management logic.
    """
    global positions, operations

    for i in range(1, len(df)):

        # Condição de entrada
        if not positions:
            # Cruzamento de Compra: MA20 > MA50
            if df['MA20'].iloc[i - 1] < df['MA50'].iloc[i - 1] and df['MA20'].iloc[i] > df['MA50'].iloc[i]:

                # Condição da MA200 (se MA200 existir e tiver valor válido)
                if 'MA200' in df.columns and df['MA200'].iloc[i] > 0:
                    positions.append('Compra')
                    operations.append({
                        'Tipo': 'Compra',
                        'Data': df['<DATE>'].iloc[i],
                        'Preco': df['<CLOSE>'].iloc[i]
                    })
                    print(f"Compra em {df['<CLOSE>'].iloc[i]} na Data {df['<DATE>'].iloc[i].date()}")

            # Cruzamento de Venda: MA20 < MA50
            elif df['MA20'].iloc[i - 1] > df['MA50'].iloc[i - 1] and df['MA20'].iloc[i] < df['MA50'].iloc[i]:

                # Condição da MA200 (se MA200 existir e tiver valor válido)
                if 'MA200' in df.columns and df['MA200'].iloc[i] > 0:
                    positions.append('Venda')
                    operations.append({
                        'Tipo': 'Venda',
                        'Data': df['<DATE>'].iloc[i],
                        'Preco': df['<CLOSE>'].iloc[i]
                    })
                    print(f"Venda em {df['<CLOSE>'].iloc[i]} na Data {df['<DATE>'].iloc[i].date()}")

        # Condição de saída (se já houver uma posição aberta)
        else:
            last_op = operations[-1]

            if last_op['Tipo'] == 'Compra':
                # Fechar Compra por ATR
                # Condição: Preço de fechamento atual < (Preço de compra - ATR)
                if df['<CLOSE>'].iloc[i] < (last_op['Preco'] - df['ATR'].iloc[i]):
                    positions.pop()
                    operations.append({
                        'Tipo': 'Fechamento Compra',
                        'Data': df['<DATE>'].iloc[i],
                        'Preco': df['<CLOSE>'].iloc[i],
                        'Lucro/Prejuizo': df['<CLOSE>'].iloc[i] - last_op['Preco']
                    })
                    print(f"Fechar Compra em {df['<CLOSE>'].iloc[i]} na Data {df['<DATE>'].iloc[i].date()}")

            elif last_op['Tipo'] == 'Venda':
                # Fechar Venda por ATR
                # Condição: Preço de fechamento atual > (Preço de venda + ATR)
                if df['<CLOSE>'].iloc[i] > (last_op['Preco'] + df['ATR'].iloc[i]):
                    positions.pop()
                    operations.append({
                        'Tipo': 'Fechamento Venda',
                        'Data': df['<DATE>'].iloc[i],
                        'Preco': df['<CLOSE>'].iloc[i],
                        'Lucro/Prejuizo': last_op['Preco'] - df['<CLOSE>'].iloc[i]
                    })
                    print(f"Fechar Venda em {df['<CLOSE>'].iloc[i]} na Data {df['<DATE>'].iloc[i].date()}")



def ATR(df, period=23):
    """
    Calculate the Average True Range (ATR) for the given DataFrame.
    """
    df['H-L'] = df['<HIGH>'] - df['<LOW>']
    df['H-PC'] = abs(df['<HIGH>'] - df['<CLOSE>'].shift(1))
    df['L-PC'] = abs(df['<LOW>'] - df['<CLOSE>'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=period).mean()
    df.drop(columns=['H-L', 'H-PC', 'L-PC', 'TR'], inplace=True)
    return df

if __name__ == "__main__":
    main()