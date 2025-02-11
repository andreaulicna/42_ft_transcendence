class CapacityConverter:
    regex = '4|8|16|32'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return str(value)