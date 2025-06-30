import chardet

class EncodingDetector:
    @staticmethod
    def detect_encoding(file_path):
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            if encoding is None:
                encoding = 'utf-8'
            return encoding
