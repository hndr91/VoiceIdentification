### Requirement

1. Install PyAudio `pip install PyAudio`
2. Install py-webrtcvad `pip install webrtcvad`
3. Install python_speech_features `pip install python_speech_features`
4. Install Scikit-learn `pip install -U scikit-learn`
5. Install Scipy

### How to Use
Run this following command

`python main.py -D <duration> -S <subject> -N <n-trial>`

### To Do
1. Detect voice activity automatically.
Currently, the voice activity limited to the duration arguments.
2. Voice identification still not implemented yet
3. Combine with RFID as identifier
4. Use AWS Polly and AWS Lex as voice user interface
