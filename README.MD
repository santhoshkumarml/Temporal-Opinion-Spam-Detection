# Temporal Opinion Spam Detection by Multivariate Indicative Signals
 Online consumer reviews reflect the testimonials of real people, unlike advertisements. As such, they have critical impact on potential consumers, and indirectly on businesses. According to a Harvard study (Luca 2011), +1 rise in star-rating increases revenue by 5–9%. Problematically, such financial incentives have created a market for spammers to fabricate reviews, to unjustly promote or demote businesses. In this work, we approach the opinion spam problem with a temporal formulation. Specifically, we monitor a list of carefully selected indicative signals of opinion spam over time and design efficient techniques to detect and characterize abnormal events in real-time. Experiments on datasets from three different review sites demonstrate that our approach is fast, effective, and practical to be deployed in real world systems.

 This is a work from  [Data Analytics Techniques Algorithms (DATA) Lab] (http://www3.cs.stonybrook.edu/~datalab/index.html) of [Computer Science Department](http://www.cs.stonybrook.edu/) at [Stony Brook University](http://www.stonybrook.edu/) under Professor [Leman Akoglu] (http://www3.cs.stonybrook.edu/~leman/) by [Santhosh Kumar Manavasi Lakshminarayanan] (https://sites.google.com/a/cs.stonybrook.edu/smanavasilak/) and  [Junting Ye] (http://www3.cs.stonybrook.edu/~juyye/)

# DataSet:
We used an Itunes Dataset and an anonymous popular ecommerce website review dataset. For Datasets please contact Professor [Leman Akoglu] (http://www3.cs.stonybrook.edu/~leman/)

## USAGE:
To Run the system with Itunes Dataset : 
###
    python -m "main.testItunes" csvFolder
For Any other dataset, consumers can create their own data reader utility similar to Temporal-Opinion-Spam-Detection/SpamDetection/util/data_reader_utils/itunes_utils/ItunesDataReader.py and run the system by following steps:

### STEP 1:
Generate and save statisitcs using the following function in Temporal-Opinion-Spam-Detection/SpamDetection/main/AppUtil
####
     extractAndSerializeBnssStatisticsForBnss(csvFolder, plotDir, timeLength = '1-W', rdr=[Your Data Reader])

### STEP 2:
Detect Anomalies by using the following function in Temporal-Opinion-Spam-Detection/SpamDetection/main/AppUtil
####
    detectAnomaliesForBnsses(csvFolder, plotDir, threshold, doPlot=True, dologStats=True)

### CONTRIBUTORS:

[Santhosh Kumar Manavasi Lakshminarayanan] (https://sites.google.com/a/cs.stonybrook.edu/smanavasilak/)

[Junting Ye] (http://www3.cs.stonybrook.edu/~juyye/)
