from flask import Flask 
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

SCORECARD_TITLE = "MASTER BRACKET - Sign Ups"
JUDGE_TITLE = "JUDGE%d"

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("Copy of Optimized Prelim Procedure (OPP) - Sample/Public Work")
scorecard = next(ws for ws in sheet.worksheets() if ws.title == SCORECARD_TITLE)

app = Flask(__name__)


def retrieve_sheet(title):
	return next(ws for ws in sheet.worksheets() if ws.title == title)

# FUNCTION TO ADD COMPETITOR TO SPREADSHEET
@app.route("/add/<competitor_name>/")
def insert_competitor(competitor_name):
	competitors = scorecard.col_values(2)
	index = len(competitors)
	# print scorecard.cell(index, 2)
	print "inserting %s" % competitor_name
	if competitor_name in competitors:
		return "cannot add %s twice" % competitor_name
	scorecard.update_cell(index+1, 2, competitor_name)	
	return "added %s" % competitor_name

# # REMOVE COMPETITOR - INCOMPLETE NEEDS TO ACCOUNT FOR BROKEN REFERENCES IN JUDGE CHARTS
# def remove_competitor(competitor_name):
# 	names = scorecard.col_values(2)
# 	index = next (i for i in range(len(names)) if names[i] == competitor_name)
# 	scorecard.delete_row(index+1)

@app.route("/score/<int:judge_id>/<string:competitor_name>/<int:score>")
def score_competitor(judge_id, competitor_name, score):
	judge_sheet = retrieve_sheet(JUDGE_TITLE % judge_id)
	print judge_sheet.col_values(2)
	names = scorecard.col_values(2)
	try:
		index = next (i for i in range(len(names)) if names[i] == competitor_name)
		judge_sheet.update_cell(index, 3, score)
	except Exception as e:
		return "Could not find competitor %s" % competitor_name
	return "Judge %d scored %s %d" % (judge_id, competitor_name, score)
	# print score

# NEED TO ACCOUNT FOR TIES
@app.route("/top/<int:n>")
def get_top_scores(n):
	competitor_dict = {}
	competitors = scorecard.col_values(2)[2:]
	average_scores = scorecard.col_values(6)[2:]
	for i in range(len(competitors)): 
		competitor_dict[competitors[i]] = average_scores[i]
	# print sorted(competitor_dict.items(), key=lambda x:-1*float(x[1]))
	top_scores = sorted(competitor_dict.items(), key=lambda x:-1*float(x[1]))[:n]
	## handle for ties
	print top_scores
	return str(top_scores)

if __name__ == "__main__":
	app.run()