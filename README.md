# Script tuning
*Read this in other languages: [한국어](docs/README_ko.md)*

- Purpose for make more natural TTS services by modifying scripts. 
- Used **Pykospacing, kiwipiepy, pdfplumber, tkinter, clova-stuido-api**

---------------

## Composition
- ### Comma
  - Insert comma for natural TTS script.
  - When test with simple RNN, but not working due to unbalanced data.
  - => Adopted clova-studio-api which fine-tuned model.
  - Convert text to csv and use clova-studio-api by tkinter gui.
  - PoC results: with human check, accuracy could be over 99%.
  
------------------------------

- ### venv script tuning
  - Preprocessing for extract pdf to text  
  - Use pykospacing, kiwipiepy, pdfplumber
  - Rule-based pdf parsing and text processing