import pandas as pd

file_path = 'EURUSD_M5_3.csv'

columns_to_drop = ['<TICKVOL>', '<VOL>', '<SPREAD>']

# Lista para armazenar as operações como dicionários
operations = []
# Lista para gerenciar a posição aberta
positions = []
POINT_VALUE = 0.00001


# Parametros de configuracao
mm200Apoio = 0

df_result = pd.DataFrame()

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


def AnaliseResultados(df):
    """
    Analisa os resultados das operações e calcula o lucro/prejuízo.
    """
    global valorFinanceiro, operation, gains
    operation = 0
    gains = 0
    valorFinanceiro = 0

    if df is None or df.empty:
        print("DataFrame está vazio ou nulo.")
        return

    if 'Lucro/Prejuizo' not in df.columns:
        print("A coluna 'Lucro/Prejuizo' não foi encontrada no DataFrame.")
        return

    # Itera sobre o DataFrame, que agora contém apenas operações de fechamento.
    for index, row in df.iterrows():
        # Verifique se a linha é um fechamento de operação
        if 'Fechamento' in row['Tipo']:

            # Adiciona o valor do lucro/prejuízo total
            valorFinanceiro += row['Resultado $$']
            operation += 1

            # Se for um ganho, incrementa a contagem de ganhos
            if row['Lucro/Prejuizo'] > 0:
                gains += 1

    # Imprime o relatório final apenas se houverem operações
    if operation > 0:
        print("\n--- Relatório Final ---")
        print(f"Lucro/Prejuízo Líquido: {valorFinanceiro:.5f}")
        print(f"Total de Operações: {operation}")
        print(f"Operações com Ganho: {gains}")
        print(f"Operações com Perda: {operation - gains}")
        print(f"Porcentagem de Acerto: {gains / operation * 100:.2f}%")
    else:
        print("Nenhuma operação de fechamento foi encontrada no DataFrame.")

def main():
    df = load_data(file_path)

    if df is not None:
        ma_windows = [20, 50, 200]
        df = calculate_moving_averages(df, ma_windows)

        if df is not None:
            # print(df.tail())
            df = ATR(df)
            posicao(df)
            # Convert operations to DataFrame for better visualization
            df_result = pd.DataFrame(operations)

            # calculo de lucro/prejuizo financeiro
            df_result['Resultado $$'] = df_result.apply(
                lambda row: (row['Lucro/Prejuizo']/ POINT_VALUE) if 'Lucro/Prejuizo' in row else 0, axis=1
            )
            AnaliseResultados(df_result)
            # print("Moving averages calculated successfully.")
            # print("Positions:", positions)
            # print("Results:", operations)
            # print("Final Results DataFrame:")
            print(df_result)
        else:
            print("Failed to calculate moving averages.")
    else:
        print("Failed to load data.")


def posicao(df):
    """
    Função atualizada com a correção da MA200, adição de Take-Profit e simulação de Spread.
    """
    global positions, operations

    # Definir o spread em pips. Use um valor realista para o seu ativo.
    spread = 0.00010

    # Múltiplo do ATR para o Take-Profit.
    take_profit_multiple = 2

    for i in range(1, len(df)):

        # Ignorar as primeiras barras onde o ATR não está disponível
        if pd.isna(df['ATR'].iloc[i]):
            continue

        # Lógica de Entrada (se não houver posição aberta)
        if not positions:

            # Condições de Compra
            if (df['MA20'].iloc[i - 1] < df['MA50'].iloc[i - 1] and
                    df['MA20'].iloc[i] > df['MA50'].iloc[i]):
                if mm200Apoio == 1:
                    # Check MA200 para tendência de alta
                    if 'MA200' in df.columns and df['MA200'].iloc[i] > df['MA200'].iloc[i - 1]:
                        positions.append('Compra')

                        # Simular entrada com o spread
                        entry_price = df['<CLOSE>'].iloc[i] + spread
                        take_profit_level = entry_price + (df['ATR'].iloc[i] * take_profit_multiple)

                        operations.append({
                            'Tipo': 'Compra',
                            'Data': df['<DATE>'].iloc[i],
                            'Preco': entry_price,
                            'ATR_na_Entrada': df['ATR'].iloc[i],
                            'Take_Profit_Level': take_profit_level
                        })
                        # print(f"Compra em {entry_price:.5f} na Data {df['<DATE>'].iloc[i].date()}")
                else :
                    positions.append('Compra')

                    # Simular entrada com o spread
                    entry_price = df['<CLOSE>'].iloc[i] + spread
                    take_profit_level = entry_price + (df['ATR'].iloc[i] * take_profit_multiple)

                    operations.append({
                        'Tipo': 'Compra',
                        'Data': df['<DATE>'].iloc[i],
                        'Preco': entry_price,
                        'ATR_na_Entrada': df['ATR'].iloc[i],
                        'Take_Profit_Level': take_profit_level
                    })
                    # print(f"Compra em {entry_price:.5f} na Data {df['<DATE>'].iloc[i].date()}")


            # Condições de Venda
            elif (df['MA20'].iloc[i - 1] > df['MA50'].iloc[i - 1] and
                  df['MA20'].iloc[i] < df['MA50'].iloc[i]):
                if mm200Apoio == 1:
                    # Check MA200 para tendência de baixa
                    if 'MA200' in df.columns and df['MA200'].iloc[i] < df['MA200'].iloc[i - 1]:
                        positions.append('Venda')

                        # Simular entrada com o spread
                        entry_price = df['<CLOSE>'].iloc[i] - spread
                        take_profit_level = entry_price - (df['ATR'].iloc[i] * take_profit_multiple)

                        operations.append({
                            'Tipo': 'Venda',
                            'Data': df['<DATE>'].iloc[i],
                            'Preco': entry_price,
                            'ATR_na_Entrada': df['ATR'].iloc[i],
                            'Take_Profit_Level': take_profit_level
                        })
                        # print(f"Venda em {entry_price:.5f} na Data {df['<DATE>'].iloc[i].date()}")
                else:
                    positions.append('Venda')

                    # Simular entrada com o spread
                    entry_price = df['<CLOSE>'].iloc[i] - spread
                    take_profit_level = entry_price - (df['ATR'].iloc[i] * take_profit_multiple)

                    operations.append({
                        'Tipo': 'Venda',
                        'Data': df['<DATE>'].iloc[i],
                        'Preco': entry_price,
                        'ATR_na_Entrada': df['ATR'].iloc[i],
                        'Take_Profit_Level': take_profit_level
                    })
                    # print(f"Venda em {entry_price:.5f} na Data {df['<DATE>'].iloc[i].date()}")

        # Lógica de Saída (se houver uma posição aberta)
        else:
            last_op = operations[-1]
            current_close = df['<CLOSE>'].iloc[i]

            # Fechar Compra
            if last_op['Tipo'] == 'Compra':
                # Condição para Stop-Loss ou Take-Profit
                stop_loss_level = last_op['Preco'] - last_op['ATR_na_Entrada']

                if current_close < stop_loss_level or current_close >= last_op['Take_Profit_Level']:
                    positions.pop()
                    operations.append({
                        'Tipo': 'Fechamento Compra',
                        'Data': df['<DATE>'].iloc[i],
                        'Preco': current_close,
                        'Lucro/Prejuizo': current_close - last_op['Preco']
                    })
                    # print(f"Fechamento Compra em {current_close:.5f} na Data {df['<DATE>'].iloc[i].date()}")

            # Fechar Venda
            elif last_op['Tipo'] == 'Venda':
                # Condição para Stop-Loss ou Take-Profit
                stop_loss_level = last_op['Preco'] + last_op['ATR_na_Entrada']

                if current_close > stop_loss_level or current_close <= last_op['Take_Profit_Level']:
                    positions.pop()
                    operations.append({
                        'Tipo': 'Fechamento Venda',
                        'Data': df['<DATE>'].iloc[i],
                        'Preco': current_close,
                        'Lucro/Prejuizo': last_op['Preco'] - current_close
                    })
                    # print(f"Fechamento Venda em {current_close:.5f} na Data {df['<DATE>'].iloc[i].date()}")



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