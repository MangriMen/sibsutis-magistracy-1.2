module lab1

go 1.20

require (
	example.com/images v0.0.0
	example.com/utils v0.0.0
)

replace example.com/images v0.0.0 => ../images

replace example.com/utils v0.0.0 => ../utils
