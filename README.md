# CS50’s Web Programming with Python and JavaScript - Capstone / Final Project

This application has been submitted as a project for Harvard's CS50x 'Web Programming with Python and JavaScript' class. It comprises a Python application which offers a prototype for a reporting software. The data are shown on the dashboard on tiles. Each tile shows a datafield which is a cost or profit center or a peformance indicator. All other pages are required for data, performance indicator or data field administration.


### Description
<ul>
    <li>Course description: https://cs50.harvard.edu/web/2020/</li>
    <li>Video demo: https://youtu.be/oz-h5Gzo90w</li>
</ul>

### Distinctiveness and Complexity
This paragraph has been added due to the requirements stated by the CS50 staff:<br>
The submited project exceeds the previously submitted projects in distinctiveness and complexity. The reporting application is distinct in terms of design and functionality. The design is not aligned to the layout of any previous application. As an example, color gradients have been used in the background and the color scheme differs. Additional frameworks such as chartjs have been used to render the graphics of the tiles on the dashboard. As far as the complexity is concerned, effort has been drawn to backend functionalities such as data aggregation for markets, time periods and datafields. In addition, the calculation of kpis is added as an entirely new functionality. The application makes use of the same technology as the previous applications such as AJAX and Django. Additional frameworks such as pandas have been used. The entire layout follows the idea of a responsive design. This summarizes why the submitted application is distinct and matches or exceeds previously submitted apps in terms of complexity.


### Scope
#### A. Templates & Statics
<ul>
    <li>Styles.css includes the  styling for all html templates.</li>
    <li>data.html: Page for entering data entries.</li>
    <li>datefields.html: Page entering new data fields. A datafield can be a cost center or a profit center.</li>
    <li>index.html: The dashboard including customized tiles with financial data. As a benchmark the previous year is shown. A form enables the specification of a point of time and a data aggregation type. 'Month' aggregates all data for a month. 'YTD' aggregates all data of the current year until the specified point of time. 'R12' aggregates all data of the past 12 months starting at the specified point of time.</li>
    <li>kpi.html: Page for adding performance indicators. Data field codes must be entered in ? ... ? (for example ?0001?). A data type must be set to enable a correct formatting of the data being presented on the tiles.</li>
    <li>layout.html: Layout file for all other templates. It also comprises the basic java script functionality. The navigation bar as well as the background can be edited in this file.</li>
    <li>login.html: Page including the login form.</li>
    <li>register.html: Page including the registration form.</li>
</ul>

#### B. Django Files in Dashboard app of Financials project
<ul>
    <li>views.py: File comprises the python application code. Django forms shown on html pages are defined here.</li>
    <li>urls.py: File listing all routes.</li>
    <li>models.py: File including all django models which form the basis for the sql database.</li>
</ul>
