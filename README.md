# Calligram Documentation and Examples
<img src="logo.png" alt="drawing" width="200"/>

## Installation

```bash
git clone git@github.com:Shelby-Company-Ltd/Calligram-Documentation.git
```

## Yelp Fusion API Example

As an example of how to use the Calligram API in an end-to-end application, we have provided an example script, `bin/run.py`, along with an example endpoint configuration file, `config/yelp.json`, that allow users to run natural language queries against the [Yelp Fusion API Business Search](https://www.yelp.com/developers/documentation/v3/business_search) endpoint.

### Usage

In order to run the script, you must first obtain a Calligram API key and a Yelp Fusion API key. You can obtain a Calligram API key by signing up on the website [here](https://www.calligram.io/account). You can obtain a Yelp Fusion API key by following the instructions outlined [here](https://www.yelp.com/developers/documentation/v3/authentication).


Once you have obtained the API keys, set them as environment variables like so:
```bash
export CALLIGRAM_API_KEY="YOUR_CALLIGRAM_API_KEY"
export YELP_API_KEY="YOUR_YELP_API_KEY"
```

The script can then be run as follows
```bash
./bin/run.py "YOUR_NATURAL_LANGUAGE_QUERY"
```

For example, in order to find cheap coffee shops in NYC, you could run:
```bash
./bin/run.py "Show coffee shops open now in NYC with a price range of \$."
```
NOTE: "$" must be escaped in the natural language query.

## Building Your Own Endpoint Configurations

Calligram can be used to generically parse parameters specified in the Calligram `map` request body. See the [official API documenation](https://www.calligram.io/documentation) for more information and `config/yelp.json` for an example of the `name` and `parameters` objects.