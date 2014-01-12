import decimal
import math
from decimal import Decimal

def float_to_decimal(f):
    
    # http://docs.python.org/library/decimal.html#decimal-faq
    "Convert a floating point number to a Decimal with no loss of information."

    n, d = f.as_integer_ratio()
    numerator, denominator = Decimal(n), Decimal(d)
    ctx = decimal.Context(prec=60)
    result = ctx.divide(numerator, denominator)

    while ctx.flags[decimal.Inexact]:
        ctx.flags[decimal.Inexact] = False
        ctx.prec *= 2
        result = ctx.divide(numerator, denominator)

    return result

def round_sf(number, sigfig):

    # http://stackoverflow.com/questions/2663612/
    # nicely-representing-a-floating-point-number-in-python/2663623#2663623
    "Round a number to a certain amount of significant digits."

    # First, it must be made certain that the number of significant digits to
    # be rounded to is greater than zero
    assert(sigfig > 0)

    # The number is then converted to a decimal number
    try:
        d=decimal.Decimal(number)
    except TypeError:
        d=float_to_decimal(float(number))
        
    # Separate the number given into three strings: a sign (0 for +/1 for -),
    # the digits as an array, and the exponent.
    sign,digits,exponent = d.as_tuple()
    
    # Case 1: if the amount of digits is less than the amount of significant
    # digits desired, we must extend it by adding zeros at the end of the
    # number until we have the amount of digits desired.
    if len(digits) < sigfig:
        digits = list(digits)
        digits.extend([0] * (sigfig - len(digits)))
    
    # Create a variable "shift" and set it equal to the new exponent of the
    # number after adding zeros.
    shift = d.adjusted()
    
    # Set a new variable, result, equal to an integer of all numbers up to
    # the desired number of digits.
    result=int(''.join(map(str, digits[:sigfig])))
    
    # Round the result if the number of digits is greater than that desired.
    # Look at the number to the right of the last desired digit and decide
    # if rounding up is necessary. Since "result" does not contain a decimal,
    # we can simply add 1 to the current value of result.
    if len(digits) > sigfig and digits[sigfig] >= 5: result += 1
    
    # Set result to a list of strings of its digits (an array)
    result = list(str(result))
    
    # Rounding can change the length of result.
    # If so, adjust shift by the difference between the length of the new
    # result and the amount of sigfigs desired.
    shift += len(result) - sigfig
    
    # Reset length of result to sigfig; chip off the extra digit if we may
    # have just added one on. Otherwise, result remains unchanged..
    result = result[:sigfig]
    
    if shift >= sigfig - 1:
        # Tack more zeros on the end if we shortened the number by rounding it
        # This occurs if the number. 
        result += ['0'] * (shift-sigfig+1)
    elif 0 <= shift:
        # Place the decimal point in between digits if our number contained
        # digits after the decimal
        result.insert(shift+1, '.')
    else:
        # Tack zeros on the front if our number was less than zero originally
        assert(shift < 0)
        result = ['0.'] + ['0']*(-(shift+1)) + result

    if sign:
        result.insert(0, '-')

    return ''.join(result)

def round_unc(number, unc, **kwds):
    
    """Round an uncertainty value to 1 or 2 sigfigs and output the number
    rounded to its uncertainty"""

    if 'form' in kwds.keys():
        outputform = kwds['form']
    else:
        outputform = 'SI'

    if 'crop' in kwds.keys():
        sigfig_crop = kwds['crop']
    else:
        sigfig_crop = 0

    number = str(number)

    if Decimal(number) < 0:
        nsign = 1
    else:
        nsign = 0

    if Decimal(unc) < 0:
        return 'WARNING:: UNCERTAINTY LESS THAN ZERO. TRY AGAIN'

    # Search for scientific notation markers (FORTRAN and Maple compatible),
    # and replace them with 'e'
    number = str(number).replace('E', 'e').replace('D', 'e').replace('Q', 'e')\
                        .replace('-','')
    unc = str(unc).replace('E', 'e').replace('D', 'e').replace('Q', 'e')

    # Create a new number that is the uncertainty to two significant digits,
    # replacing zeros, decimals, and negative signs with blank spaces
    unc_tosigfigz = round_sf(unc, 2).replace('0', '').replace('.', '')\
                                    .replace('-', '')

    if len(unc_tosigfigz) == 1:
        unc_tosigfigz += "0" # We want two digits in our uncertainty

    # If the uncertainty is now greater than 30, read only one significant
    # figure.
    # Now change the uncertainty to include only the correct amount of
    # significant digits.
    if Decimal(unc_tosigfigz) >= Decimal(sigfig_crop): 
        unc_sigfigz=1
        unc_tosigfigz=round_sf(unc_tosigfigz,unc_sigfigz).replace('0','')
    else: # Otherwise, read two
        unc_sigfigz=2
        unc_tosigfigz=round_sf(unc_tosigfigz,unc_sigfigz)

    unc = round_sf(unc, unc_sigfigz)

    # Find the decimal place in both the uncertainty and the number.
    # When all is said and done, we want both numbers to have the same
    # amount of digits in relation to the decimal place ?? **REVISE**
    uncdecplace = unc.find('.')
    numdecplace = number.find('.')

    # First case; if the uncertainty is a float value
    if uncdecplace != -1:
        uncafterdec = len(list(unc)[uncdecplace+1:])

        # Case 1a; the uncertainty is a float, but the number is an
        # integer. Need to add a decimal and zeros for rounding and
        # reset the numdecplace variable.
        if numdecplace==-1:
            number=''.join(list(number)+['.']+['0']*(uncafterdec+1))
            numdecplace = number.find('.')

        # Case 1b; the uncertainty and number are both floats. Need
        # to add only zeros to the number for rounding.
        else:
            number=''.join(list(number)+['0']*uncafterdec)
            numdecplace = number.find('.')

        # Since the uncertainty is a float, it will have digits
        # after the decimal place.
        result = ''.join(number[:numdecplace + uncafterdec + 1])\
                   .replace('.', '')
        result = list(result)

        i = 0
        zeros = 0
        if result[0] == '0':
            for i in range(len(result)-1):
                if result[i] == '0':
                    zeros = zeros + 1
                    i = i + 1
                else:
                    break

        result = ''.join(result)
        # Doing some rounding in the number
        if int(list(number)[numdecplace + uncafterdec + 1]) >= 5:
            result = '0'*zeros + str(int(result) + 1)

        result = list(result)

        numafterdec = len(list(result)[numdecplace + 1:])

        # If we've shortened the number by rounding it, add on a zero
        # to match the amount of digits after the decimal in the
        # uncertainty.
        if int(numafterdec) < int(uncafterdec):
            result += ['0']*(int(uncafterdec) - int(numafterdec) - 1)

        # Replacing negative sign if needed
        result.insert(numdecplace, '.')
        if nsign:
            result.insert(0,'-')

        result = ''.join(result)
        
        return result

    # If the uncertainty has no decimal place
    elif uncdecplace == -1:

        # Adding a decimal to the uncertainty
        unc = ''.join(list(unc) + ['.'])

        # Locate decimal place in the number and uncertainty
        if numdecplace == -1:
            number = ''.join(list(number) + ['.'])
            numdecplace = number.find('.')

        uncdecplace = unc.find('.')

        if unc_sigfigz == 2:
            # Count trailing zeros
            zeros = len(list(unc)[2:uncdecplace])

            # Trimming result to correct place
            result = ''.join(list(number)[:numdecplace - zeros])
            number = ''.join(list(number)[:numdecplace - zeros + 2])\
                       .replace('.','') + '0'*5

            # Round the number if necessary
            if int(number[numdecplace - zeros]) >= 5:
                result = str(int(result) + 1)
            else:
                result = str(result)

            # Insert trailing zeros again
            result = list(result[:numdecplace - zeros])
            result += ['0']*int(zeros)
            if nsign:
                result.insert(0,'-')
            result = ''.join(result)

            return result

        elif unc_sigfigz == 1:
            zeros = len(list(unc)[1:uncdecplace])

            result = ''.join(list(number)[:numdecplace - zeros])\
                       .replace('.', '')

            numnodec = ''.join(list(number)).replace('.', '')
            numnodec += '000'

            if int(list(numnodec)[numdecplace - zeros]) >= 5:
                result = str(int(result) + 1)

            result = list(result)
            result += ['0']*int(zeros)
            if nsign:
                result.insert(0,'-')
            result = ''.join(result)

            return result

def sp_loc(result,numdecplace):
            # Finding where spaces are needed in the answer, once every 3 digits
        space_locations1 = [0]
        space_locations = []

        # ans_dec-2 is used because we need the numbers BEFORE the decimal
        for i in range(int(numdecplace)/3):
            space_locations1.append(1 + (numdecplace+2)%3 + 3*i)

        # isolating the numbers AFTER the decimal
        for i in range((len(str(result)) - numdecplace)/3):
            space_locations.append(numdecplace + 3*(i+1))
        
        if space_locations1[len(space_locations1)-1] != int(numdecplace):
            space_locations1.append(numdecplace)

        # Adding spaces into the answer
        new_ans=""
        for i in range(len(space_locations1) - 1):
            if i==(len(space_locations1) - 2):
                a = int(space_locations1[i])
                b = int(space_locations1[i + 1])
                new_ans = new_ans+str(result)[a:b]
            else:
                a = int(space_locations1[i])
                b = int(space_locations1[i + 1])
                new_ans = new_ans+str(result)[a:b] + ' '

        try:
            space_locations[len(space_locations)-1]
        except IndexError:
            space_locations.append(len(result))
        else:
            if len(result)-1 != space_locations[len(space_locations)-1] and\
            len(result) != space_locations[len(space_locations)-1]:
                space_locations.append(len(result))

        if len(space_locations) == 1:
            a = int(space_locations1[len(space_locations1) - 1])
            b = int(space_locations[len(space_locations) - 1])
            new_ans=new_ans+str(result)[a:b+1]+' '
        elif len(space_locations)==2:
            a=int(space_locations1[len(space_locations1)-1])
            b=int(space_locations[0])
            new_ans=new_ans+str(result)[a:b+1]+' '
            a=int(space_locations[len(space_locations)-1])
            new_ans=new_ans+str(result)[b+1:a+1]+' '
        else:
            for i in range(len(space_locations)-1):
                a=int(space_locations[i])
                if i==0:
                    b=int(space_locations1[len(space_locations1)-1])
                    new_ans=new_ans+str(result)[b:a+1]+' '
                    b=int(space_locations[i+1])
                    new_ans=new_ans+str(result)[a+1:b+1]+' '
                elif i==len(space_locations)-1:
                    b=int(space_locations[i+1])
                    new_ans=new_ans+str(result)[a+1:b+1]
                else:
                    b=int(space_locations[i+1])
                    new_ans=new_ans+str(result)[a+1:b+1]+' '
        new_ans=new_ans[:-1]
        
        return new_ans

def roundit(number, unc, **kwds):

    """Round a number and its uncertainty to match and print the output in
    SI form"""

    # Search for scientific notation markers (FORTRAN and Maple compatible),
    # and replace them with 'e'
    number = str(number).replace('E', 'e').replace('D', 'e').replace('Q', 'e')

    # Find the decimal place in the number
    number = round_sf(number,len(number))
    numdecplace = number.find('.')

    # If no decimal in the number, insert one at the end
    if numdecplace == -1:
        number+='.'
        numdecplace = number.find('.')

    # If the user enters an integer as an uncertainty, round it to that amount
    # of significant figures and return with warning
    if isinstance(unc,int) == True:
        print "** WARNING:: INTEGER UNCERTAINTY TAKEN AS NUMBER OF "+\
        "SIGNIFICANT FIGURES ("+str(unc)+") **"
        return round_sf(number,unc)

    # Search for scientific notation markers and replace with 'e'. Must do this
    # with unc after it has been tested to see if it is an integer
    unc = str(unc).replace('E', 'e').replace('D', 'e').replace('Q', 'e')

    if Decimal(unc) < 0:
        return 'WARNING:: UNCERTAINTY LESS THAN ZERO. TRY AGAIN'

    # Check for a form and assign to variable
    if 'form' in kwds.keys():
        outputform = kwds['form']
    else:
        outputform = 'SI'

    # Check for a crop value and assign to variable
    if 'crop' in kwds.keys():
        sigfig_crop = kwds['crop']
    else:
        sigfig_crop = 0

    # Ensure that the number is a string
    number = str(number)

    # Create a new variable, set as the uncertainty to two significant digits,
    # replacing zeros, decimals, and negative signs with blank spaces
    unc_tosigfigz = round_sf(unc,2).replace('0','').replace('.','')\
                                   .replace('-', '')

    # Ensure there are two digits in the uncertainty value for cropping
    if len(unc_tosigfigz) == 1:
        unc_tosigfigz+="0"

    # If the uncertainty is now greater than crop value, change the uncertainty
    # to include only one significant digit
    if Decimal(unc_tosigfigz) >= Decimal(sigfig_crop): 
        unc_sigfigz=1
        unc_tosigfigz=round_sf(unc_tosigfigz,unc_sigfigz).replace('0','')
    else:
        unc_sigfigz=2
        unc_tosigfigz=round_sf(unc_tosigfigz,unc_sigfigz)

    if outputform == 'SI':
        result = sp_loc(round_unc(number,unc,crop=str(sigfig_crop),\
                        form=str(outputform)),numdecplace)
    else:
        result = round_unc(number,unc,crop=str(sigfig_crop),\
                           form=str(outputform))

    # Round the uncertainty to the proper amount of significant digits for use
    # with plusminus and tuple output forms
    unc=round_sf(unc,unc_sigfigz)

    if outputform == 'SI':
        if is_number(result[len(result)-2]) == True:
            return ''.join(result)+'('+str(unc_tosigfigz)+')'
        elif result[len(result)-2] == ' ':
            if len(unc_tosigfigz) == 2:
                return ''.join(result)+'('+str(unc_tosigfigz[0])+' '\
                          +str(unc_tosigfigz[1])+')'
            elif len(unc_tosigfigz) == 1:
                return ''.join(result)+'('+str(unc_tosigfigz[0])+')'
        elif result[len(result)-2] == '.':
            if len(unc_tosigfigz) == 2:
                return ''.join(result)+'('+str(unc_tosigfigz[0])+'.'\
                          +str(unc_tosigfigz[1])+')'
            elif len(unc_tosigfigz) == 1:
                return ''.join(result)+'('+str(unc_tosigfigz[0])+')'
    elif outputform == 'plusminus':
        return ''.join(result)+' +/- '+str(unc)
    elif outputform == 'tuple':
        return [result,unc]

def is_number(s):

# http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-in-python

    try:
        float(s)
        return True
    except ValueError:
        return False