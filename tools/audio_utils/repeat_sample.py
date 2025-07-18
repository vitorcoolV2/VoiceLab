import argparse
import librosa
import soundfile as sf
import numpy as np
import os
import sys

parser = argparse.ArgumentParser(description="Repete um sample WAV várias vezes para criar um arquivo mais longo.")
parser.add_argument("--input", "-i", required=True, help="Arquivo WAV de entrada")
parser.add_argument("--output", "-o", required=True, help="Arquivo WAV de saída")
parser.add_argument("--repeat", "-r", type=int, default=30, help="Número de repetições (default: 30)")
args = parser.parse_args()

# Verifica se o arquivo de entrada existe
if not os.path.isfile(args.input):
    print(f"[ERRO] Arquivo de entrada '{args.input}' não encontrado.")
    print("Verifique o nome e o caminho do arquivo e tente novamente.")
    sys.exit(1)

try:
    # Carrega o sample
    print(f"Carregando {args.input}...")
    y, sr = librosa.load(args.input, sr=None)
except Exception as e:
    print(f"[ERRO] Não foi possível carregar o arquivo '{args.input}': {e}")
    sys.exit(1)

# Repete o sample
print(f"Repetindo {args.input} {args.repeat} vezes...")
y_long = np.tile(y, args.repeat)

# Salva o novo arquivo
try:
    print(f"Salvando arquivo longo em {args.output}...")
    sf.write(args.output, y_long, sr)
    print("Arquivo criado com sucesso!")
except Exception as e:
    print(f"[ERRO] Não foi possível salvar o arquivo '{args.output}': {e}")
    sys.exit(1) 