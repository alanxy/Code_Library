# code_library
A PyQt application centralizing different files/ scripts with a csv file as the database.

The inside structure of the application is identical to the one in code.csv. Functions could be added under different sections. For example, for the function UST checking put under UST under Bond (Bond > UST > UST checking), it should be put in order in the csv file as shown in the image.

<!-- ![alt text](https://github.com/alanxy/code_library/blob/master/UST_level.PNG "UST checking") -->

There are a total of 10 levels that could be added and is possible to extend. After a blank column, there are three columns, namely description, directory and require_input.
1. desctiption: a simple description on your functionality, where you type in the csv will be reflected in the application.
2. directory: the full directory to your source file. The applcation currently support csv and py file. It will open csv file with Excel or directly run a python file.
3. require_input: if your source file is a py file which requires some simple input, type some hints in the csv and there will be an input box poped up in the application requring you to type some input. The input will be passed to the py file as arguments. If your source file is not a csv file or a py file that does not require an input, just leave it blank.

(excel & GUI screenshot to be added)

Restart the program after you make changes.
