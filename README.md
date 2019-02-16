# Zendesk Extraction Tool
## Summary
This project initially started as a simple script to parse Zendesk ticket exports into comments and tags for machine learning. Now this is a multi tool for parsing and data aggregation of tickets. Flask and Pandas are needed to run.
## DEPRECATED Pseudocode
>  * Create an array to contain our modified json objects
>  * Import the json file
>  * Parse the file into an array of individual JSON objects
>  * For each object in the array:
>    * Extract the ```ticket.brand_id``` (integer)
>    * Extract the ```ticket.id``` (integer)
>    * Extract the ```ticket.description``` (string)
>    * Extract the ```ticket.tags``` (string array)
>    * If ```ticket.status``` is "closed"
>      * Store values in a new JSON object and append that object to our array
>  * Return the new array of modified json objects
