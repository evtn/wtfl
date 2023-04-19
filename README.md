# WTFL — Well-designed Text-based Friendly Language

This is a spec for a very well-designed declarative language and a Python package to work with it.    
Obviously, current solutions for config et al. (JSON, YAML, TOML) are very unsuitable as software development progress is going on, so here I propose a brand new format.   

WTFL has all the features of its predecessors, and much more, with a very well-designed friendly syntax.

It is case-insensitive, obvious and feature-rich language.

Here is an example of the format:

```wtfl
...This is a comment

key's "value"

weight of apple is 123
```

This is equivalent to this JSON:

```json
{
    "key": "value",
    "apple": {
        "weight": 123
    }
}
```

# Package

Package's API is similar to built-in `json`:

read an object from a string:
```python
def wtfl.loads(
    s, # string to load
    *,
    parse_float, # function for float parsing, `float` used by default
    parse_int, # function for integer parsing (only unprefixed decimal), `int` used by default
    parse_roman, # function for roman numerals parsing, accepts whole literal as a string (0r...)
    parse_numbers, # function for integer literals parsing (0b..., 0o..., and so on)
) -> 
```
read an object from a file (same argument meaning as `.loads`):    
`wtfl.load(file, *, parse_float, parse_int, parse_roman, parse_numbers)` 

dump an object into a string:
```python
def wtfl.dumps(
    obj: object, # object to dump
    *,
    # if True, non-serializable keys / values are skipped
    skipkeys: bool = False, 
    
    # if True, encodes non-ASCII characters
    ensure_ascii: bool = True, 
    
    # if a non-negative integer, used as indent size. if a string, used as indent character. If None, everything is inlined
    indent: int | str | None = 2, 
    
    # a function that is used to recover from serialization errors. 
    # if current value is not serializable and skipkeys=False, tries to serialize the result of default(value)
    default: Callable[[object], str] | None = None, 
    
    # if True, sorts object keys
    sort_keys: bool = False,
)
```
dump an object into a file (same argument meaning as `.dumps()`):    
`wtfl.dump(file, obj, *, skipkeys, ensure_ascii, indent, default, sort_keys)`

# Reserved keywords

It is very important to know all the keywords of WTFL, since all those keywords are important.    

Here's a list (keywords in the same list entry are equivalent and used interchangeably in the spec):

- `is` / `are` / `'s` / `'re` / `do` / `does` / `be`
- `isn't` / `aren't` / `'sn't` / `'ren't`
- `of`
- `also` / `and also` / `but also`
- `that` / `this` / `these` / `those`
- `there`
- `have` / `has` / `'ve`
- `haven't` / `hasn't` / `'ven't`
- `can`
- `cannot` / `can't`
- `true` / `falsen't`
- `false` / `truen't`
- `and`
- `return`
- `skip`
- `stay`
- `to`

You can use keywords as names (except true / false / haven't), this list is just so you know them all.

# Keys

Keys are at the center of the language. In WTFL, keys are defined in two ways:

1. Same as values. Provide a value and it will be converted to string.
2. As bare name. A bare name should start with any char of `[A-Za-z_-]` and consist of chars in `[A-Za-z0-9_-]`.

Any key can have optional piece preceding it. Possible choices are: `a`, `an`, `the`, `de`, `du`, `le`, `la`, `les`, `des`, `but` and `um`.

Here are some examples:

```wtfl
32 is 32
0x45 is 0x45
4.5's 4.5
"key2" be "key2"
the jasdofia913247 is "what?"
a mogu's "sus"
```

It's equivalent to this JSON:

```json
{
    "32": 32,
    "69": 69,
    "4.5": 4.5,
    "key2": "key2",
    "jasdofia913247": "what?",
    "mogu": "sus"
}
```

# Inline

```
Many formats, such as TOML, don't allow writing everything in one line. That's a shame, since, as we all know, writing everything in one line greatly improves readability and this block is a living proof of that rule. You can easily read everything written here without any discomfort, so why restrict a language to multiple lines?
```

Since inlining is so good, WTFL introduces it in a very simple manner, just write everything in one line:

```wtfl
apple does have weight is 123 color is "red" that is everything you need to know about apples but also key is 123
```
(With one exception: array/object definitions have to end in newline or `also`)


Is equivalent to this JSON:

```json
{
    "apple": {
        "weight": 123,
        "color": "red"
    },
    "key": 123
}
```

# Values

## Setting values

Setting values to keys is straightforward using `is` (or `are` or any other alias):

```wtfl
key is 35
key2 be 0x56
```

This sets "key" to 35. But there are various other ways.

For example, if you are sure key has to have some value, use `has to be` or `have to be`:

```wtfl
key has to be 35

key is 36 ...no!!!! this would raise some error.
```

If you want to say the key can have some value, use `can be`:

```wtfl
key can be 35

key is 36 ...well, okay, good luck next time
```

...or `can't be` / `cannot be` for opposite meaning:

```wtfl
key can't be 35

key is 35 ...what? you just said it can't be! error here
```

You also can just allow and restrict keys:
```wtfl
key can be
key2 can't be

key is 23 ...okay
key2 is 23 ...nope
```

Be sure to not mess up the order (see Time Travel section for workarounds):

```wtfl
key is 23

key can't be 23 ...produces a warning "Too late, it's already done", but no error (since it's already done)
```

Setting key several times makes a lot of sense, but only the last value is preserved (see Time Travel section for workarounds)

```wtfl
key is 23
key is 35

...The key is 35 now
```

## Types

### Numbers

There are decimal integer literals, such as `102`, `-4`, `0`, and, as expected, some other:

- Binary (2) with `0b` prefix: `0b10010`
- Octal (8) with `0o` prefix: `0o755`
- Decimal (10) with `0d` prefix: `0d102`
- Duodecimal (12) with `0z` prefix: `0z9a1`
- Vigesimal (20) with `0v` prefix: `0vjija`
- Roman numerals with `0r` prefix: `0rXIMI`

Floats are also supported: `0.1`, `2.`, `.2`, `2.3e4`, `2.3e4`

### Strings

String literals are enclosed in double quotes, supporting all the usual Python escape sequences:

```wtfl
sus is "amogus"
```

### None / null

...is represented by `haven't` keyword:

```wtfl
value is haven't
```

Equivalent to:

```json
{
    "value": null
}
```

### Boolean

That type is very simple: You have `true` / `falsen't`, and you have `false` / `truen't`

### Objects

Nested structures are often needed, so WTFL has those!

Suppose you have this JSON:

```json
{
    "apple": {
        "weight": 123,
        "color": "red"
    }
}

```

Here's how you define this complex object with WTFL, using `have` / `has` keyword:

```wtfl
apple does have
    weight is 123
    color is "red"
that's all folks!
```
Indentation is optional, as well as the exclamation mark after "that's all folks".
In fact, you can use any line to end the object, as long as it starts with `(that|there)`:

```wtfl
that's all
that is everything, folks
there's nothing more I think
there are no more keys, go home
there it is, the end of the object!
```

Be aware that you cannot use `also` in that line (see Inline section for more info)

If you want something less structured, you can define keys one-by-one:

```
weight of apple is 123
color of apple is "red"
```

### Arrays

As any good format, WTFL has arrays. Arrays are defined very straightforwardly:

```wtfl
apple_crate does have
    has
        weight is 123
        color is "red"
    that was the object
    
    23 ...what? a number in apple crate? okay...
        
that was the array
```

Equivalent JSON:

```json
{
    "apple_crate": [
        {
            "weight": 123,
            "color": "red"
        },
        23
    ]
}
```

Be aware that...

```wtfl
has
that's all
```

...is an empty object. If you want an empty list, use:

```wtfl
has 0
```

If you create an array and then add a non-integer key, it will turn into an object:

```wtfl
apple_crate does have
    has
        weight is 123
        color is "red"
    that was the object
    
    23 ...what? a number in apple crate? okay...
        
that was the array

frog of apple_crate is 10
```

Produces:

```json
{
    "apple_crate": {
        "0": {
          "weight": 123,
          "color": "red"
        },
        "1": 23,
        "frog": 10
      }
}
```

Keys less than 0 are ignored, keys greater than array length are added, but moved so that there's no holes in the resulting array.


# Advanced features

## Time travel

It is very obvious that there has to be a time travel feature in a modern config format.    
You can travel to the past, to the future, and (experimental) to the present

### Past

To travel to the past, use `return` keyword:

```wtfl
key is 24

...1 is offset in statements. Your statement will be transported right before `key is 24`
return 1 and key can't be 24 
```

This would raise an error, because key can't be 24 at line 1

### Future

To travel to the future, use `skip` keyword:

```wtfl
skip 2 and key is 35

key is 24
```

This would set key to 35, because statement 0 is transported two statements forward, after `key is 35`. 

### Present

This is highly experimental. Use at your own risk.

You can stay in the present (not travelling anywhere)

```wtfl
stay and key is 35

key is 24
```

### Possible problems

1. If you travel back in time and kill your parents, you will never be born
    This is sad, but doesn't influence WTFL
    
2. If you travel back in time and kill my parents, I will never be born
    Please don't exploit this critical vulnerability

3. If you travel in the same line several times, you will create a chain of events inside a single time point. Maybe that's what you want, maybe all bees are aliens. I can't know everything.



# Caveats

- I've decided to not add dates / time support, because of the time travel (and possibly date travel)