# SearchThroughOCR

This repository provides a convenient way to extract text from images and PDF files using Optical Character Recognition (OCR) technology. By leveraging the power of Google API and OpenAI, you can efficiently search through PDF files or images and create spreadsheets from the extracted text.

## Prerequisites

To use this repository, you need to have the following:

1. An account on Google API (for OCR functionality).
2. An account on OpenAI (for enhanced text processing).
3. Access keys for both Google API and OpenAI.

## Installation

1. Clone this repository to your local machine.

```bash
git clone https://github.com/your-username/SearchThroughOCR.git
```

2. Install the necessary dependencies using pip.

```bash
pip install -r requirements.txt
```

## Usage

To extract text from images, use the following command:

```bash
python search.py -i [image-name|images-folder]
```

For example:

```bash
python search.py -i image.jpg
```

```bash
python search.py -i images-folder/
```

To extract text from PDF files, use the following command:

```bash
python search.py -f [file-name|folder-name]
```

For example:

```bash
python search.py -f document.pdf
```

```bash
python search.py -f folder-name/
```

**Note:** When providing folder names, use forward slashes ("/") to specify the path, even on Windows systems. For example: `c:/folderName`.

## Acknowledgements

This project utilizes the power of Google API and OpenAI to provide advanced OCR capabilities. We acknowledge their contribution to the development of this repository.

## License

This project is licensed under the [MIT License](LICENSE). Feel free to modify and distribute this code for personal or commercial use.
