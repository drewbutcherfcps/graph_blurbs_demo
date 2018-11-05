### Comments for graphBlurbs.json file ###
1. name is the name of the graph this is used for your reference only and does not affect any of the code
2. id is the id of the graph found when you edit a graph in the dashboard
3. graphStory is displayed inside the first dropdown text under what story is this chart telling
4. chartType is a reference to the chart type named in the graphInterpretations.json file
5. dataQualityReason is the first question in the third dropdown text
6. dataQualityLinkContent is the answer to dataQualityReason
7. dataQualityLinkUrl is the link for the answer dataQualityLinkContent
8. contactEmail is the second part under the third dropdown text.  This is a reference to someone to contact if there are question.  In the python script the name is used to produces a fayette county email address, this will need to be changed for your school.
9. contactSubjectLine is the third part under the third dropdown text
10. goodUseOfVisualization is the fourth part under the third dropdown text
11. externalReferences are references at the bottom of the info panel

     
### Comments for graphInterpretations.json file ###
1. This produced the content for the second dropdown.  
2. Citation is build in for those who want to cite a reference.  
3. Obtain authors permission if you are reproducing someone elses work.    

On the Dasbhoard navigate to ***Site Administration > Services > Dashboard Services*** and click Edit

In the field Page Disclaimer under Disclaimer Setting add a script tag with a CDN to JQuery-UI this is for the draggable function.  This can be found at https://code.jquery.com/ui/       
