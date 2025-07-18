from pathlib import Path

def print_feedback_speaker_missing(speaker, registered_speakers):
    """Feedback quando o speaker não existe no servidor."""
    print(f"❌ Speaker '{speaker}' não existe no servidor.")
    suggest_register_command(speaker)
    print_speakers_list(registered_speakers)
    list_local_samples()

def print_endpoint_called(method, path):
    """Mostra o endpoint chamado (método + path)."""
    print(f"➡️  Endpoint chamado: {method.upper()} {path}")

def suggest_register_command(speaker):
    """Sugere comando para registar um speaker."""
    print("Sugestão: Registe o speaker com:")
    print(f"  python3 talk.py --define-speaker {speaker} --voice-sample caminho/para/{speaker}.wav --speaker-props lang=pt desc=\"Voz {speaker} demo\"")

def list_local_samples():
    """Lista samples .wav locais disponíveis."""
    samples = list(Path(".").glob("*.wav"))
    if samples:
        print("Samples .wav locais disponíveis:")
        for s in samples:
            print(f"  {s}")

def print_success_speaker_registered(speaker):
    """Feedback de sucesso ao registar speaker."""
    print(f"✅ Speaker '{speaker}' registado com sucesso!")

def print_speakers_list(registered_speakers):
    """Lista speakers registados."""
    if registered_speakers:
        print(f"Speakers registados atualmente: {list(registered_speakers.keys())}")
    else:
        print("Não há speakers registados atualmente.")

def print_error_and_exit(msg, endpoint=None):
    """Mostra erro e endpoint, depois termina o programa."""
    print(f"❌ {msg}")
    if endpoint:
        print_endpoint_called(*endpoint)
    exit(1) 