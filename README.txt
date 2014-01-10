Module: Sigfig v0.1
Developed by: Michael Busuttil, Travis Valdez
Last Updated: Friday, January 10, 2014

Usage:

1) float_to_decimal(f)
	- Used to convert a floating point number, f, to a Decimal with no loss
	of information

	*Examples:
	>>> float_to_decimal(12.34567)
	Decimal('12.3456700000000001438138497178442776203155517578125')

	>>> float_to_decimal(12.34567936495037565930245649)
	Decimal('12.3456793649503762111407922930084168910980224609375')

2) round_sf(number, sigfig)
	- Used to round a number (number) to a certain amount of significant
	figures (sigfig)

	*Examples:
	>>> round_sf(12.3456,1)
	'10'

	>>> round_sf(12.3456,2)
	'12'

	>>> round_sf(12.3456,3)
	'12.3'

	>>> round_sf(12.3456,4)
	'12.35'

3) round_unc(number, unc, **kwds)
	*Possible Keywords:
		a) form:
			i) SI outputs: numbertosigfigs(uncertainty)
			ii) plusminus outputs: numbertosigfigs +/- uncertainty
			iii) tuple output: [numbertosigfigs,uncertainty]
		b) crop: specifies the number under which the uncertainty is
		rounded to two significant figures, and over which the uncer-
		tainty is rounded to one significant figure

	- Used to round an uncertainty (unc) to the proper crop value, round
	the number (number) to match the uncertainty, and return the number
	in the proper form

	*Examples:
	>>> round_unc(1234,1)
	'1234'

	>>> round_unc(1.234567,0.0001234)
	'1.2346'

	>>> round_unc(1.234567,0.0001234,crop=30)
	'1.23457'

4) sp_loc(result, numdecplace)
	- Used to insert the "spaces" into a number (result) being output
	in SI form

	*Examples:
		>>> sp_loc('1001',4)
		'1 001'

		>>> sp_loc('1.234567',1)
		'1.234 567'

5) roundit(number, unc, **kwds):
	*Possible Keywords:
		a) "form = ____"
			i) "SI" **default** : numbertosigfigs(uncertainty)
			ii) "plusminus": numbertosigfigs +/- uncertainty
			iii) "tuple": [numbertosigfigs,uncertainty]
		b) crop: specifies the number under which the uncertainty is
		rounded to two significant figures, and over which the uncer-
		tainty is rounded to one significant figure.
			- NOTE: DEFAULT IS 0

	- Used to round an uncertainty (unc) to the proper crop value, round
	the number (number) to match the uncertainty, and return the number
	and the uncertainty in the proper form
		- NOTE: THIS FUNCTION IS PERFORMED ONLY IF THE UNCERTAINTY
		VALUE IS NOT AN INTEGER. IF THE UNCERTAINTY IS AN INTEGER
		VALUE, ENTER IT AS A STRING (Ex. 1 --> '1')
	- Used to round a number (number) to a specified amount of significant
	figures (unc)
		- NOTE: THIS FUNCTION IS PERFORMED ONLY IF THE UNCERTAINTY
		VALUE IS AN INTEGER

	*Examples:
		>>> roundit(1234,1)
		**WARNING:: INTEGER UNCERTAINTY VALUE --> ROUNDED TO**
		**1 SIGNIFICANT FIGURE(S)**
		'1 000'

		>>> roundit(1234,'1')
		'1 234(1)'

		>>> roundit(1.234567,0.0001234)
		'1.234 6(1)'

		>>> roundit(1.234567,0.0001234,crop=30)
		'1.234 57(12)'

		>>> roundit(1.234567,0.0001234,crop=30,form="plusminus")
		'1.234 57 +/- 0.00012'

		>>> roundit(1.234567,0.0001234,crop=30,form="tuple")
		['1.234 57', '0.00012']

