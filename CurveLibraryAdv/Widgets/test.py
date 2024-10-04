def main():
    case01 = "III"
    case02 = "LVII"
    case03 = "MCMXCIV"

    romanToInt( case03 )

def romanToInt( s ):
    num = 0
    values = []
    master = { 'I':1, 'V':5, 'X':10, 'L':50, 'C':100, 'D':500, 'M':1000 }
    maths = []

    for i in range(len(s)):
        values.append( master[s[i]])
    
    for i in range(len(s)):
        if i != 0:
            if values[i-1] < values[i]:
                print( f"{values[i-1]} < {values[i]}" )
                maths.append('-')
            else:
                print( f"{values[i-1]} == {values[i]}" )
                maths.append('+')
    
    print(values)
    print(maths)

        

main()