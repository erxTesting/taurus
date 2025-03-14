# Apiritif
Allows running load and functional Python tests using [Apiritif test framework](https://github.com/Blazemeter/apiritif),
which is based on [Nose library](https://nose.readthedocs.io/en/latest/index.html).
You can run Nose tests the following way:
```yaml
execution:
- executor: apiritif
  scenario:
    script: test_nose.py
```
Also, if not present, Taurus creates and stores Nose test to the artifacts directory, when Apiritif executor is used.

Taurus can loop test suite execution in a loop until desired number of `iterations` will complete or `hold-for` time
will be exceeded.

Usage:
```yaml
execution:
- executor: apiritif
  scenario:
    script: tests/
```

It allows you to use some logic blocks:
- `transaction`: collect requests in one block
- `set-variables`: set/change value of variable
- `include-scenario`: include scenario into another one
- `setup`: list of initial requests
- `teardown`: list of final requests (will be executed even if previous is failed)

and CSV data sources. Use following format to specify them:
```yaml
scenarios:
  sample:
    variables:
      var1: val1
    requests:
    - setup:
        - http://init.com
        - http://login.com
    - http://blazedemo.com     # ordinal request
    - transaction: second   # transaction
      do:
      - http://blazedemo.com/send
      - http://blazedemo.com/receive/${var1} # get 'receive/val2'
      - set-variables:  # change variable value
          var1: val2
      - http://blazedemo.com/receive/${var1} # get 'receive/val2'
    - include-scenario: inner
    - teardown:
        - http://logout1.com
        - http://logout2.com

    data-sources: # these are data-sources options for Apiritif. See more info below.
    - path/to/my.csv  # this is a shorthand form
    - path: path/to/another.csv  # this is a full form
      delimiter: ';'
      quoted: false
      loop: true
      variable-names: id,name

  inner:
    requests:
    - set-variables:
        var1: val3
    - http://blazedemo.com/receive/${var1}
```
See more info about data-sources [here](DataSources.md).

It is valid to specify both single Python module (single .py file) and a Python package (folder with Python modules
and packages).

Configuration options:

```yaml
modules:
  apiritif:
    working-dir: classes  # set name of runner working directory within artifacts dir
    interpreter: /home/user/interpreter/python  # path to custom interpreter.
```
## Scenario
Apiritif executor supports building test script from the `requests` option of `scenario`. In that case Taurus will
generate a Python script that will be launched with `apiritif`.

With `Apiritif` executor you can ask for Selenium browser test with `test-mode` option:

```yaml
execution:
- executor: apiritif
  test-mode: selenium
```

In `selenium` mode follow request features are supported:

  - `browser` for the following browser types: Chrome, Firefox, Ie, Opera, Android-Chrome, iOS-Safari, Remote
  - `remote` for local webdriver, local remote webdriver or [remote webdriver](#Remote-WebDriver)
  - `capabilities` of local and [remote webdriver](#Remote-WebDriver)
  - `request` only for GET method
      - `action` keyword for Selenium actions
      - `assert` (requested page source inspected use the new assertTitle, assertTextBy or assertValueBy* for item level)
  - `timeout` and `think-time` on both scenario and request levels

Here is the list of supported actions, sorted by action type.

### Locators
Below you will see some actions, which look like this: `actionX`, i.e. `dragByX`, `clickBy`, etc. Here `X` means a certain
action object. It can be one of the following: `CSS`, `Element`, `ID`, `LinkText`, `Name`, `XPath`. For example, `clickByID`,
`waitForByName`, `keysByCSS`.

#### How to find them
__1. By ID__

```html
<td>
    <h1 id="my_locator_ID">Locator ID</h1>
</td>
```
Header tag has an ID attribute (`id="Locator\_ID"`). For example, wait until the element is displayed `waitForByID(Locator\_ID)`.

__2. By the attribute Name__

```html
<input name="inputName">
```

This is an input element, and it has an attribute `name="inputName"`.

For example, insert text the following in the input `keysByName(inputName): First\_Name`. Locator determination by the attribute `Name` is often used when working with input fields.

__3. By CSS Selector__

CSS is used for styling different elements of an HTML webpage, to separate the content of the page and its design.
The .css files define these styles, set font size, width, height, etc. There are certain patterns in the CSS, which act
as selectors and are applied to HTML elements of the page. Selenium uses the same principle to find
items.

Here is an example. This is how to find div with input.
```html
<div class="controls">
    <input id="inputName" placeholder="First Last" name="inputName" type="text">
</div>
```
This CSS selector .controls will select all elements with class `controls`. For example, wait until the element is displayed `waitForByCSS(.controls)`.
Using attributes and their value
```html
 <input id="inputName" placeholder="First Last" name="inputName" type="text">
```

Find the element by `name="inputName"`. For example, `keysByCSS(#inputName): First Name`


__4. Using ID__

Find the field for input name with `id="inputName"`

`\<input id="inputName" placeholder="First Last" name="inputName" type="text">`

CSS selector - `#inputName`. Fox example, add text in the field `keysByCSS(#inputName): first\_name`

__5. Child elements__
```html
<div class="controls">
    <input id="inputName" placeholder="First Last" name="inputName" type="text">
</div>
```
Find child element INPUT with `id="inputName"` in the div with `class="controls"`. Describe as `div.controls>input#inputName`. For example, `keysByCSS(div.controls>input#inputName): first\_name`

__6. By XPath__

XPath is the language used for locating nodes in an XML document. As HTML can be an implementation of XML (XHTML), Selenium can use this language to find elements for the web page. One of the main reasons for using XPath is when you don't have a suitable id or name attribute for the element you wish to locate. To locate the element we can use absolute XPath or use relative path elements that have attributes id, name etc.

For INPUT
```html
<div class="controls">
    <input placeholder="First Last" type="text">
</div>
```

We can compose following XPath expressions:
 - `//div/input`
 - `//div\[@class="controls"]/input`

Any of these expressions can be used to fetch the desired element, if these attributes are unique.

__7. By Shadow Locator__

Shadow Locator enables to work with Shadow DOM which is designed as a tool for building component-based 
applications. For example Salesforce Lightning Component Library is based on Shadow DOM. 
Shadow DOM is self-contained and thus simple locators will not return nodes inside it.

Shadow Locator is composed by a sequence of css selectors, e.g.:

```html
shadow: c-basic, lightning-accordion-section, .slds-button
```

The last CSS Selector refers to the target element in a shadow tree. 
The preceding CSS Selectors refer to the shadow hosts.

Most of the actions in Apiritif support Shadow Locators.

#### Alternative syntax supporting multiple locators
It is possible to specify multiple locators for each action. This helps to increase script resiliency. If a locator
fails (e.g. because of a webpage change and the script was not updated to reflect the changes) an alternative locator
will be used. If no locator succeeds then the script fails.
All the locators above are supported, i.e. `ID`, `Name`, `LinkText`, `CSS`, `XPath`.


This is an example how it looks like:
```yaml
  - type: select  # action name
    param: American Express # parameter for the select action
    locators:     # list of locators for the action, these are attempted one by one from top to bottom
      - id: select_id           # locator types are case-insensitive
      - css: another_class    
      - xpath: absolute_xpath
      - xpath: relative_xpath   # there may be multiple locators of the same type
      - name: select_name
```
You can see full example [here](#Sample-scenario-using-multiple-locators).

### Keywords
Below you can find a list of all supported actions:

[alert](#Alert), [answerDialog](#Answering-dialogs), [assertDialog](#Assertions), [assertEval](#Assertion), 
[assertTextByX](#Assertion), [assertTitle](#Assertion), [assertValueByX](#Assertion), [clearCookies](#Cookies), 
[clickByX](#Mouse-actions), [closeWindow](#Window-management), [contextClickByX](#Mouse-actions), 
[doubleClickByX](#Mouse-actions), [dragByX](#Mouse-actions), [echoString](#Echoing), [editContentByX](#Editing), 
[foreach](#Foreach), [go](#Go), [if](#If-Blocks), [keysByX](#Typing), [log](#External-logging), [loop](#Loops), 
[mouseDownByX](#Mouse-actions), [mouseOutByX](#Mouse-actions), [mouseOverByX](#Mouse-actions), 
[mouseUpByX](#Mouse-actions), [openWindow](#Window-management), [rawCode](#Execution), [screenshot](#Screenshot), 
[scriptEval](#Execution), [selectByX](#Select), [storeEval](#Store), [storeString](#Store), [storeTextByX](#Store), 
[storeTitle](#Store), [storeValueByX](#Store), [submitByX](#Typing), [switchFrame](#Frame-management), 
[switchWindow](#Window-management), [typeByX](#Typing), [waitForByX](#Pause).

#### Alert
For alert handling, use the following methods:
- `alert("OK")` to click "OK" on an alert
- `alert("Dismiss")` to dismiss alert
 
Besides, you can use [alternative syntax](#Alternative-syntax-supporting-multiple-locators):

```yaml
- type: alert
  param: OK
```

For additional operations with dialogs see [Dialogs management](#Dialogs-management).

#### Assertion
For requested page source inspection you can use the following actions:
- `assertTextByX(X\_name): "text"` to assert text to an element
- `assertValueByX(X\_name): value` to assert value
- `assertTitle(title)` to assert page title
- `assertEval(js_expr)` to assert that evaluation of a JavaScript expression returns true value

Don't forget to replace `X` with the right [locators](#Locators).
See sample usage in [Frame Management](#Frame-management) section.

For assertion, you can also use special assertion block. See example [here](#Sample-scenario).

Using the [alternative syntax](#Alternative-syntax-supporting-multiple-locators): 
```yaml
- type: assertText
  param: text
  locators:
    - id: element_id
    - xpath: /xpath
- type: assertValue
  param: value
  locators:
    - id: element_id
- type: assertTitle
  param: title
- type: assertEval
  param: js_expr
```

#### Cookies
To delete all cookies use `clearCookies()` action.

The same can be written like this: 
```yaml
- type: clearCookies
```

#### Dialogs management
Besides, the basic functionality to handle [Alerts](#Alert) it is also possible to use the
following actions to do assertion and answering on Dialogs.

##### Assertions

Enables to check whether a dialog of a specified type was previously displayed with the 
given message. The type can be any of the following: `alert`, `prompt` or `confirm`.

Examples:

```yaml
- assertDialog(alert): Error occurred
- assertDialog(prompt): Enter your name
- assertDialog(confirm): Are you sure to proceed?
```

Example using the Alternative syntax:

```yaml
- type: assertDialog
  param: alert
  value: Error occurred
```

##### Answering dialogs

Allows to set the value that will be returned by displaying a dialog. It is applicable
to `alert`, `prompt` and `confirm` dialogs. This action actually prevents showing the dialog and instead
returns the specified value directly.

For alert dialogs the value needs to be always '#Ok' for dismissing the dialog.
For confirmation dialogs the value can only be either `'#Ok'` or `'#Cancel'`, meaning to simulate 
click on 'Ok' or 'Cancel' buttons.

Examples:

```yaml
- answerDialog(alert): '#Ok'
- answerDialog(prompt): John Doe
- answerDialog(confirm): '#Cancel'
```

Examples using the alternative syntax:

```yaml
- type: answerDialog
  param: alert
  value: '#Ok'
- type: answerDialog
  param: prompt
  value: Jon Doe
- type: answerDialog
  param: confirm
  value: '#Cancel'
```

#### Echoing
Use `echoString("echoed text")` to print text string on the Apiritif output execution.

Or you may use:
```yaml
- type: echoString
  param: echoed text
```

#### Editing
`editContentByX(X\_name): "new test for X"` will help you change text in an editable field.

Or by using the [alternative syntax](#Alternative-syntax-supporting-multiple-locators):
```yaml
- type: editContent
  param: new text for X
  locators:
    - css: element_class
```

#### Execution
For execution of a non-yaml code you can use the following options:
- `scriptEval("script")` to execute JS command like this
```yaml
scriptEval("alert('This is a JavaScript command.');")
```
Which can be written also like:
```yaml
- type: scriptEval
  param: alert('This is a JavaScript command.')
```
- `rawCode: Python code` to insert python code as it is.
```yaml
rawCode: print('This is a python command.')
```

```yaml
- type: rawCode
  param: print('This is a python command.')
```

See example [here](#Sample-scenario).

#### Foreach

`foreach` blocks allow iterating over each element on a page that matches the specified `locators`.

For example:

```yaml
scenarios:
  example:
    browser: Chrome
    timeout: 10s
    requests:
      - label: example_foreach_1
        actions:
          - go(http://blazedemo.com)
          - foreach: el             # specify the name of the variable that will be used in the actions referring that element
            locators:
              - css: input
              - xpath: //input
            do:
              - clickByElement(el)  # refers to the variable el 
              - typeByElement(el): text to type
              - type: storeValue
                element: el         # refers to the variable el
                param: my_var
                             
```

`locators` is an array of selectors equivalent to those used in 
[alternative syntax notation](#Alternative-syntax-supporting-multiple-locators).
The `locators` also work the same way - the selectors in the array are examined 
one by one and which first returns a not empty set of elements is used then for the iteration.

To refer to the given element in the current iteration you need to use either 
the suffix `ByElement` for the short version of actions notation or `element` for the alternative version.
This way explicit locators (e.g. `ById`, `ByXpath`) are replaced by reference to the variable you define
in the `foreach` loop. You however can still use the explicit locators combined with the `ByElement` actions in 
the loop. See the example below.

```yaml
scenarios:
  example:
    browser: Chrome
    timeout: 10s
    requests:
      - label: example_foreach_2
        actions:
          - go(http://blazedemo.com)
          - foreach: el             # specify the name of the variable that will be used in the actions referring that element
            locators:
              - css: input
              - xpath: //input
            do:
              - clickByElement(el)  # refers to the variable el 
              - dragByElement(el): elementById(id_123)
              - keysById(btn_submit): KEY_ENTER
```

You can also nest multiple `foreach` blocks, just make sure to 
use unique names for the variables in each of the blocks.  

Please note that it is not possible to use `waitFor` action in the `foreach` using `ByElement`. 
However, you can still use it inside the loop the common way - e.g. `waitForById(my_id)`.

##### Perform actions in foreach using the parent context

It is possible to specify in each action inside the foreach loop additional set of locators besides just the `element` field.
This way it allows to locate a child element within the parent `element`.

In the following example we iterate over table rows and do a click action on
the button that should be located on each row.

```yaml
scenarios:
  example:
    browser: Chrome
    timeout: 10s
    requests:
      - label: example_foreach_context
        actions:
          - go(http://blazedemo.com)
          - foreach: el             
            locators:
              - css: table_row
              - xpath: //tr
            do:
              - type: click
                element: el
                locators:         # the list of locators that to find the child element in the parent 'el'
                  - css: .btn-small
                  - css: .button-small
```

Note that this is only supported while using the  
[alternative syntax](#Alternative-syntax-supporting-multiple-locators) for the action.

#### Frame management
When you need to perform actions on elements that are inside a frame or iframe, you must use the `switchFrame` command
to activate the frame before perform any action.

Sample usage:
```yaml
scenarios:
  sample_frame:
    requests:
    - url: http://a-frame-sample.com
      actions:
      - switchFrame(index=0) # Select First Frame
      - assertTextByCSS(body): "First Frame Body"
      - switchFrame(relative=parent) # Go to parent
      - switchFrame(index=1) # Select Second frame
      - switchFrame(index=0) # Nested Frame, Select the First frame inside the Top Second frame
      - assertTextByID(content): "First Frame Body inside Second Frame Body"
      - switchFrame(relative=top) # Go to top frame (main document)
```
Note: For first level frames, it is possible to use `switchFrameByX` and using selector to match the frame to switch or 
to provide the selector inside the switchFrame action. Both of these syntaxes generate the same output.

```yaml
  - switchFrameByCss(.cls)
  - switchFrame(css=.cls)

  - switchFrameByName(frame_name)
  - switchFrame(name=frame_name)

  - switchFrameById(frame_id)
  - switchFrame(id=frame_id)

  - switchFrameByXpath(//xpath)
  - switchFrame(xpath=//xpath)
```

Disclaimer: Currently there are problems in the support of this functionality by geckodriver and chromedriver, depending on the case to test some of these methods can generate a failure, mainly in cases where you have nested frames or frames mixed between frame and iframes.

It is also possible to use the alternative syntax for Frame management, however there is currently no support for multiple locators:
```yaml
- type: switchFrame
  param: index=0
- type: switchFrame
  param: relative=parent

- type: switchFrame
  param: name=frame_name
- type: switchFrame
  param: id=frame_name
- type: switchFrame
  param: css=.cls
- type: switchFrame
  param: xpath=//xpath
```

#### Go
Use `go(url)` to redirect to another website.
```yaml
- type: go
  param: url
```

#### If Blocks

Apiritif allows controlling execution flow using `if` blocks. These blocks enable 
conditional execution of actions.

Each `if` block should contain a mandatory `then` field, and an optional `else` field. Both `then` and `else` fields
should contain list of actions.

Here's a simple example:

```yaml
scenarios:
  example:
    browser: Chrome
    variables:
      elem_id: id_123
    timeout: 10s
    requests:
      - label: example1
        actions:
          - go(http://blazedemo.com)
          - if: 'document.getElementById("${elem_id}") !== undefined'
            then:
              - clickById(${elem_id})
            else:
              - go(http://blazedemo.com/login)
```

Logic blocks can also be nested:

```yaml
scenarios:
  nested_example:
    requests:
      - label: nested_req
        actions:
          - if: <condition1>
            then:
              - if: <condition2>
                then:
                  - go(https://google.com/)
                else:
                  - go(https://yahoo.com/)
            else:
              - go(https://bing.com/)
```

Note that `<conditions>` are evaluated as JavaScript code, so they must contain valid JavaScript expression 
that yields boolean value.

#### Loops

`Loop` blocks allow repeated execution of actions. 

It is necessary to specify variable name used in the loop,
along with the `start` and `end` indexes. The actions that shall be executed in the loop are defined in the `do` field.
In these action you can then reference the variable by the name you defined next to the `loop` keyword.
 
Optionally you can set the `step` field which defines the difference between each number in the sequence 
(it can also be negative). If `step` is not explicitly set then it will default to 1.

```yaml
scenarios:
  example:
    browser: Chrome
    timeout: 10s
    requests:
      - label: example_loop
        actions:
          - go(http://blazedemo.com)
          - loop: var_i
            start: 1
            end: 10
            do:
              - clickById(id_${var_i})
              - typeById(input_${var_i}): My Item ${var_i} 
``` 

Note that both the `start` and `end` index are included in the loop. So for 
example setting `start` to 1 and `end` to 5 will loop through these values: \[1, 2, 3, 4, 5\].

It is also possible to specify the `step` negative. In that case the loop will go from the higher 
numbers to the lower ones. However, it is also necessary that the `start` index is higher than the 
`end` index. 

For example:

```yaml
  - loop: i
    start: 5
    end: 1
    step: -1
    do: 
      - clickById(id_${i})
``` 
This will loop through the values \[5, 4, 3, 2, 1\] in the descending order.

Note that you may also use variables in the `start`, `end` and `step` fields. These fields may
include numbers surrounded by quotes and one can even concatenate in this case numbers with variables.

For example: 

```yaml
scenarios:
  example:
    browser: Chrome
    timeout: 10s
    variables:
      step: 1
      end: '00'
    requests:
      - label: example_loop
        actions:
          - go(http://blazedemo.com)
          - loop: i
            start: '1'
            end: '1${end}' # will result in 100
            step: ${step}
            do: 
              - clickById(id_${i}) 
``` 

#### Loop Over Data

`loopOverData` blocks allow looping over data rows of a csv file.

For example:

```yaml
 - loopOverData: cities.csv # name of the csv file to loop over
   variable: city # name of the variable that will hold the current row from the csv file
   do:
    - type: go
      param: https://www.google.com?q=${city.name}  # to reference a value, use the variable name defined above and use the dot notation
```

To use `loopOverData` you need to specify the csv file in the `data-sources` section first,
then you can reference it via either the full path or just the file name.

Optionally it is possible to use indexes `from` and `to` so that you can loop only over a subset of csv data.
You may use just one of the indexes or both in one block.

The following example will start the loop at the 5th row and ends with the 10th row, so it will loop over 6 rows.

```yaml
 - loopOverData: cities.csv 
   variable: city 
   from: 5
   to: 10
   do:
    - type: go
      param: https://www.google.com?q=${city.name} 
```

Note that the first row in a csv file has an index value of 1.

#### Mouse actions
For mouse imitating actions you can use the following:
- `clickByX(X\_name)`
- `doubleClickByX(X\_name)`
- `contextClickByX(X\_name)`
- `mouseDownByX(X\_name)`
- `mouseUpByX(X\_name)`
- `mouseOutByX(X\_name)`
- `mouseOverByX(X\_name)`
- `dragByX(X\_name): elementByX(another\_X\_name)`

`X` here is for one of [locators](#Locators).

Or by using the [multiple locators](#Alternative-syntax-supporting-multiple-locators) syntax:
```yaml
- type: click
  locators:
     - css: element_class
     - xpath: /xpath/
- type: doubleClick
  locators:
     - css: element_class
     - xpath: /xpath/
- type: contextClick
  locators:
     - css: element_class
     - xpath: /xpath/
- type: mouseDown
  locators:
     - css: element_class
     - xpath: /xpath/
- type: mouseUp
  locators:
     - css: element_class
     - xpath: /xpath/
- type: mouseOut
  locators:
     - css: element_class
     - xpath: /xpath/
- type: mouseOver
  locators:
     - css: element_class
     - xpath: /xpath/
- type: drag
  source:
    - name: element_name
    - xpath: /xpath/
  target:
    - css: element_css
    - xpath: /xpath/
```

#### Pause
For pause, you can use the following actions:

- `waitForByX(X\_name, condition): timeout`

This action allows for checking that the given object meets the `condition` within the `timeout` period. 
`timeout` value is optional, its default value is 10s.

`condition` is one of the following:

    - Present
    - Visible
    - Clickable
    - NotPresent
    - NotVisible
    - NotClickable


`timeout` is optional with default value of 10 (10 seconds). Timeout can be provided as a numeric value 
and that will mean seconds, or it can be provided as a formatted string with the pattern 
1d2h3m4s5ms where you can provide number of days, hours, minutes, seconds and milliseconds it’s required to wait. 

You can also define waitFor using the [alternative syntax](#Alternative-syntax-supporting-multiple-locators) to provide multiple locators:
```yaml
- type: waitFor
  locators: 
    - css: element_class
    - id: element_id
  param: clickable    # the condition
  value: 2m30s        # the timeout, optional parameter    
```

Supported conditions are: `present`, `visible`, `clickable`, `notpresent`, `notvisible`, `notclickable`.

- `pauseFor(time)`
```yaml
- type: pauseFor
  param: time
```

`X` here is for one of [locators](#Locators).

#### Screenshot
To take a screenshot of a viewport and save it in a file use this: `screenshot(file\_name)`

Or like this by using the [alternative syntax](#Alternative-syntax-supporting-multiple-locators):

```yaml
- type: screenshot
  param: file_name
```

#### Select
To select a value use this: `selectByX(X\_name): value`.

See documentation for `X` [here](#Locators).

Or by using the [alternative syntax](#Alternative-syntax-supporting-multiple-locators):
```yaml
- type: select
  param: value
  locators:
    - id: element_id
```

#### Store
For storing variables use the following actions:
- `storeTitle(): var_title`
- `storeString(value): "var_string"`
- `storeTextByX(X\_name): "var_text"`
- `storeValueByX(X\_name): var_value`

See documentation for `X` [here](#Locators).

For storing the result of evaluation of a JavaScript expression use:

- `storeEval(js_expr): var_eval`

The following example will store to the `el_present` variable a flag indicating
whether the find element by id was successful or not:
- `storeEval(document.getElementById("elem_id") !== undefined): el_present`

Or use the [alternative syntax](#Alternative-syntax-supporting-multiple-locators):
```yaml
- type: storeTitle
  param: var_title
- type: storeString
  param: var_string
  value: value
- type: storeText
  param: var_text
  locators:
    - id: element_id  
- type: storeValue
  param: var_value
  locators:
    - id: element_id
- type: storeEval
  param: var_eval
  value: js_expr
```

#### Typing
Typing actions are the following:
- `typeByX(X\_name): "text\_to\_type"` clears `X` value and then types text.
- `typeSecretByXX\_name): "secret"` hides the secret value in the action logging  
- `submitByX(X\_name)`
- `keysByX(X\_name): value` sends keystrokes to `X`. `value` can be formed like this: `KEY\_ENTER`. See also [Selenium with Python > WebDriver API > Special Keys](https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.common.keys).

`X` here is for one of [locators](#Locators).

Typing actions with [multiple locators support](#Alternative-syntax-supporting-multiple-locators):
```yaml
- type: type
  param: text_to_type
  locators:
    - css: input_css
    - name: input_name
- type: typeSecret
  param: mysecret
  locators:
    - name: secret_input
- type: submit
  locators:
    - id: element_id
- type: keys
  param: KEY_ENTER
  locators:
    - id: element_id  
```

#### Window management
To open new windows or tabs, use `openWindow(value)` keyword, and the `switchWindow(value)` and `closeWindow(value)` commands will allow you to manage them.

These actions require a value parameter, the possible values are:
  - `number`: The index to the window in reference, 0 is the first, 1 is the second, and so with those who want to manage. It can be also surrounded with quotes.
  - `win\_ser\_number`: Provides exactly the same functionality just like using only `number` - e.g. you can use `win\_ser\_0` to navigate to the first window
  - `name`: The name of the window (reference to the name used in the target window attribute in a link).
  - `win\_ser\_name`: In the `name` part, assign a name to the focused opened window, the next time when reference to the same window name, returns with focus to the named window selected.
  - `win\_ser\_local`: Go to the initial window.
  - `no value`: When no value is assigned, it means that the selection action is assigned over the last created window, and if the close action is used, it will also be over the last one created.

Note: When any action command opens a new window (like click on a link with target window assigned), 
the action of selecting the window must always be declared, otherwise the actions executed by the execution 
will be performed on the default window, or the last one used with `switchWindow` command.

Or using the [alternative syntax](#Alternative-syntax-supporting-multiple-locators):
```yaml
- type: openWindow
  param: value
- type: switchWindow
  param: value
- type: closeWindow
  param: value
```

### Sample scenario
```yaml
scenarios:
  request_example:
    browser: Firefox  # available browsers are:  Firefox, Chrome, Ie, Opera, Edge
    headless: true  # available only for Chrome/Firefox and only on Selenium 3.8.0+, disabled by default
    timeout: 10  #  global scenario timeout for connecting, receiving results, 30 seconds by default
    think-time: 1s500ms  # global scenario delay between each request
    default-address: http://blazedemo.com/  # specify a base address, so you can use short urls in requests
    certificate: /path/to/certficate
    passpharse: "passphrase" # if present
    requests:
    - url: /  # url to open, only get method is supported
      actions:  # holds list of actions to perform
      - waitForByCSS(body, present)
      - clickByID(mySubmitButton)
      - openWindow(http://blazedemo.com/vacation.html) # new window is created (#1)
      - resizeWindow(750, 750) # change window size to x, y
      - maximizeWindow() # change window size to maximum
      - closeWindow()      # close the second window (#1)
      - pauseFor(5s)
      - clearCookies()
      - keysByName(myInputName): keys_to_type
      - submitByName(myInputName)
      - waitForByID(myObjectToAppear, visible): 3s
      - scriptEval("alert('This is Sparta');")
      - rawCode: print('It\'s Python')  # insert as-is into script file
      - rawCode: |
          for i in range(10):           # multiline example
            if i % 2 == 0:
              print(i)
      - clickByShadow(c-basic,form-opened,#mytext)   # sample usage of shadow locator
      assert: # assert executed after actions
      - contains:
        - blazemeter  # list of search patterns
        - Trusted
        subject: body # only body subject supported
        regexp: false  # treat string as regular expression
        not: false  # inverse assertion condition
```
All action names are case-insensitive. Despite it misprint in action names or usage of unsupported actions break your scenario execution.
To avoid it you can use `ignore-unknown-actions` Apiritif flag and taurus will show warning when unknown action occurs.
```yaml
scenarios:
  sample:
    requests:
    - url: http://blazedemo.com
      actions:
      - definitelyUnknownAction(unknownSelector)
modules:
  apiritif:
    ignore-unknown-actions: True

```

### Sample scenario using multiple locators

When using multiple locators [alternative syntax](#Alternative-syntax-supporting-multiple-locators) it is possible to 
mix it with the shorter version of action definition.

```yaml
scenarios:
  request_example:
    browser: Firefox  # available browsers are: Firefox, Chrome, Ie, Opera, Edge
    headless: true  # available only for Chrome/Firefox and only on Selenium 3.8.0+, disabled by default
    timeout: 10  #  global scenario timeout for connecting, receiving results, 30 seconds by default
    think-time: 1s500ms  # global scenario delay between each request
    default-address: http://blazedemo.com/  # specify a base address, so you can use short urls in requests
    requests:
    - url: /  # url to open, only get method is supported
      actions:  # holds list of actions to perform
      - type: waitFor
        param: present
        locators:
          - css: body
          - xpath: /body/  
      - type: click
        locators:
          - id: mySubmitButton
          - linktext: Submit Form
          - css: btn_primary
      - openWindow(http://blazedemo.com/vacation.html)
      - clearCookies()
      - type: keys
        param: keys_to_type
        locators:
          - name: myInputName
      - type: submit
        locators:
          - name: myInputName
      - type: waitFor
        param: visible
        value: 2m30s
        locators:
          - id: myObjectToAppear
          - name: myObjectToAppearName
      - scriptEval("alert('This is Sparta');")
      - type: rawCode
        param: print('It\'s Python')  # insert as-is into script file
      - type: click   # sample usage of shadow locator
        shadow: 'c-basic, form-opened, #mytext'
      assert: # assert executed after actions
      - contains:
        - blazemeter  # list of search patterns
        - Trusted
        subject: body # only body subject supported
        regexp: false  # treat string as regular expression
        not: false  # inverse assertion condition
```


## Certificates
You can define a client-side certificate to your configuration via the following lines:
```yaml
- certificate: path/to/certficate
  passpharse: "passphrase" # if present
```
See example [above](#Sample-scenario).

## Variables

It is possible to define variables to be used in the script, declaring them at the scenario level.

To use it, simply in any reference to a text in the script you must declare the insertion of the variable by using ```${name}```

The use of variables can be used in many reference locations, in selectors or in values.
There are also commands that allow you to store and manipulate them.
Some of them are `storeTitle`, `storeTextBy \*`, `storeValueBy \*` and `storeString`.

Sample:
```yaml
scenario:
  sample:
    variables:
        sample: The is a sample site you can test with BlazeMeter!
    requests:
    - url: http://blazedemo.com/
      actions:
      - assertTextByCSS(body > div.jumbotron > div > p:nth-child(2)): ${sample}
      - storeTitle(): my_title
      - storeTextByXPath(//my/XPath/here): my_text
      - storeValueByXPath(//my/XPath/here): my_value
      - storeString(${my_title} love my ${my_text} with ${my_value}): final_text
```

## Remote WebDriver

It is possible to use the browser remotely using Remote WebDriver. It must be indicated as the browser name `Remote` and indicate in the `remote` property the URL in which the webdriver service is located to control the browser.

To specify the capabilities of the Remote WebDriver, it is necessary to be able to configure properties necessary for remote instantiation. You must use the `capabilities` structure where you can specify the main properties required by the remote webdriver.

Note: The capabilities are a way in which the remote service filters and selects the device or browser to be selected for the test, depending on its configuration according to the configured specifications. It is recommended to read the documentation of who provides the service.

### Commonly used capabilities

  - browserName
  - browserVersion
  - acceptInsecureCerts
  - platformName — commonly used for mobile devices

For the full capabilities list, see [Selenium WebDriver Browser Options](https://www.selenium.dev/documentation/webdriver/drivers/options/).

Note: Currently it is possible to perform basic tests in mobile browsers using the available actions commands, in the future more commands related to mobile will be incorporated to allow a better interactivity.

### Sample Remote Webdriver scenario:
```yaml
scenarios:
  request_example:
    browser: Remote
    remote: http://user:key@remote_web_driver_host:port/wd/hub
    capabilities:
      browserName: firefox  # Depends on the capabilities of the remote selenium server
      browserVersion: "95.0"
    requests:
    - url: http://demo.blazemeter.com  # url to open, only get method is supported
      actions:  # holds list of actions to perform
      - waitForByCSS(body, present)
    # ...
```
It is possible to use only the `remote` option, and in this way declare the intention to use the `browser: Remote`, allowing a more compact YAML.

Sample usage of `remote` without `browser: Remote` clause declaration:
```yaml
scenarios:
  request_example:
    remote: http://user:key@remote_web_driver_host:port/wd/hub
    capabilities:
      browserName: firefox  # Depends on the capabilities of the remote selenium server
      browserVersion: "95.0"
    requests:
    - url: http://demo.blazemeter.com  # url to open, only get method is supported
      actions:  # holds list of actions to perform
      - waitForByCSS(body, present)
    # ...
```

Here is a list of browsers which can be used as remote: `firefox`, `chrome`, `edge`.

Note that `remote` keyword can be used on module settings, execution settings, or scenario level.
For remote browser you can use [Browser Options](Selenium.md#Browser-options).

## Mobile Browsers

It is also possible to perform tests on mobile browsers. Currently, the browsers supported are `Chrome-Android` and `Safari-iOS`.
Mobile test services are provided by Appium, and it is possible to use Appium locally or some remote Appium service through the Remote WebDriver capability.

Note: Taurus provides the ability to provide Appium provisioning support, it is recommended to read the documentation related to [Selenium Executor / Appium](Selenium.md#appium)

### Sample Mobile Browser scenario:
```yaml
scenarios:
  request_example:
    browser: Chrome-Android
    capabilities:
      device: id_device # set the id of the device here (adb devices)
      remote: custom_appium_url # You can specify a custom url
    timeout: 10  #  global scenario timeout for connecting, receiving results, 30 seconds by default
    think-time: 1s500ms  # global scenario delay between each request
    default-address: http://demo.blazemeter.com  # specify a base address, so you can use short urls in requests
    requests:
    - url: /  # url to open, only get method is supported
      actions:  # holds list of actions to perform
      - waitForCSS(body, present)
      - clickByID(mySubmitButton)
      - pauseFor(5s)
      - clearCookies()
      - keysByName(myInputName): keys_to_type
      - waitForByID(myObjectToAppear, visible)
      assert: # assert executed after actions
      - contains:
        - blazemeter  # list of search patterns
        - Trusted
        subject: body # only body subject supported
        regexp: false  # treat string as regular expression
        not: false  # inverse assertion condition

services:
- appium
- android-emulator

modules:
  android-emulator:
    avd: android10_arm128
```

## Reporting
It is recommended to incorporate the use of the `final-stats` module with the option enabled `summary-labels` to have a better vision of results.
It will allow to visualize the status of the tests, the average time per transaction and to visualize the errors that may occur in webdriver and other components involved in the test.

Sample configuration:
```yaml
reporting:
- module: final-stats
  summary-labels: true
```
Sample output:
```
+-----------------+--------+---------+----------+-------+
| label           | status | success | avg time | error |
+-----------------+--------+---------+----------+-------+
| Find Flights    |   OK   | 100.00% |  10.581  |       |
| Reserve Flight  |   OK   | 100.00% |  1.276   |       |
| Purchase Flight |   OK   | 100.00% |  4.951   |       |
| Thanks          |   OK   | 100.00% |  0.062   |       |
+-----------------+--------+---------+----------+-------+
```

### Flow Markers

Functional test execution in the cloud requires additional metadata about the tests,
which can be provided by flow markers. Flow markers are little pieces of code added
by the Taurus to the test script that provide more data for the test execution engine.
Generating flow markers is disabled by default and enabled only for `browser: Remote`.

You can enable/disable it manually with `generate-flow-markers` option.
It can be used on both scenario-level and settings-level.

```yaml
scenarios:
  request_example:
    browser: Chrome
    generate-flow-markers: true  # scenario-specific setting
    requests:
    - url: http://blazedemo.com/
      actions:
      - waitForByCSS(body, present)
      - clickByID(mySubmitButton)
      - pauseFor(5s)

modules:
  apiritif:
    generate-flow-markers: true  # global setting
```

### External Apiritif plugins

This feature can be used to track actions of your test. It requires handler which will be executed
between actions. Please see handler [example](https://github.com/Blazemeter/apiritif/blob/master/tests/resources/action_plugin_template.txt)

To enable Apiritif plugins you should specify path to plugins package using `plugins-path` in apiritif module settings.
```
modules:
  apiritif:
    plugins-path: /path/to/apiritif/plugins/package
```
