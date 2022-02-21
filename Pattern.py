from Color import Color

class Pattern:

    #Note that this constructor is not meant to be called directly, but instead will be called when loading a pattern from a .ACNH file
    def __init__(self, title:str, author:str, town:str, palette: 'list[Color]', pattern_matrix: 'list[list[Color]]') -> None:
        if len(title) > 20:
            raise ValueError("The title of this pattern cannot be longer than 40 characters")
        if len(author) > 10:
            raise ValueError("The author name for a pattern cannot be longer than 10 characters")
        if len(town) > 10:
            raise ValueError("The town name cannot be longer than 10 characters")
         
        #While the color pallete also includes a 16th value, the transparent pixel, this is implicit and thus is not a part of the passed palette
        if len(palette) != 15:
            raise ValueError("The pallete must contain exactly 15 color objects")
        
        if len(pattern_matrix) * len(pattern_matrix[0]) != 1024:
            raise ValueError("The Pattern Matrix must contain exactly 1024 values")
        
        self.title = title
        self.author = author
        self.town = town
        self.palette = palette
        self.pattern_matrix = pattern_matrix
    
    @staticmethod
    def load_from_file(file:str):
        with open(file, "rb") as f:
            f.read(16) #For some odd reason the .acnh file starts with 20 useless bits
            title = f.read(40).decode("UTF-16")

            f.read(4) #These bytes contain the Island ID, which we dont need
            island_name = f.read(20).decode("UTF-16")
            f.read(8) #These bytes contain 4 unknown bytes and the Author ID

            author_name = f.read(20).decode("UTF-16")
            f.read(12) #These bytes bring us to the end of the header

            palette = []
            for x in range(15):
                color_bytes = f.read(3)
                palette.append(Color.acnh_from_rgb(color_bytes[0], color_bytes[1], color_bytes[2]))
        
        print(repr(palette))
        print(title, island_name, author_name)

        """
        for x in range(20):
            byte = f.read(1)
            print(int.from_bytes(byte, byteorder="little"))
        """

if __name__ == "__main__":
    Pattern.load_from_file("/home/henry/Documents/ANCHPatternInputer/Test Binaries/Color Palletes/Default_Pallete_No_Title.acnl") 