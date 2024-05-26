# Script tuning
- Purpose for make more natural TTS services by modifying scripts. 
- used **Pykospacing, kiwipiepy, pdfplumber, tkinter, clova-stuido-api**

---------------

## Composition
- ### venv script tuning
  - Preprocessing for extract pdf to text  -
  - Use pykospacing, kiwipiepy, pdfplumber

------------------------------

- ### Comma
  - Make comma for natural TTS script.
  - When test with simple RNN, but not working due to unbalanced data.
  - => Adopted clova-studio-api which fine-tuned model.
  - Convert text to csv and use clova-studio-api by tkinter gui.
  - With human check, accuracy could be over 99%.
------------------------------
