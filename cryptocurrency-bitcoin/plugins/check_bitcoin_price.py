#!/usr/bin/env python

import argparse
import nagiosplugin
import requests
import json

class Bitcoin(nagiosplugin.Resource):
    def probe(self):
        """Called by the check controller. Contains necessary actions to retrieve metrics.
           Returns a list of metric objects and the applicable contexts they are for"""

        metrics = self.retrieve_metrics() # Dictionary of different currencies

        if(args.mode == "GBP") or (args.mode == "USD"):
           return nagiosplugin.Metric("Bitcoin_Price_" + args.mode, metrics[args.mode], context="threshold_context", uom=args.mode)
        elif args.mode == "All":
            metrics_output = []
            for i in metrics:
                metrics_output.append(nagiosplugin.Metric("Bitcoin_Price_" + i, metrics[i], context="threshold_context",
                                       uom=i))
            return metrics_output
        else:
           raise nagiosplugin.CheckError("Incorrect mode option. See help text (-h).")

    def retrieve_metrics(self):
        """Requests JSON data from coindesk API and returns results as a dictionary"""

        metrics = {} # Initialise dictionary for different currencies

        # HTTP Get Request for JSON data
        response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
        json_data = json.loads(response.text)

        # For each currency we want, save it to the dictionary
        metrics["GBP"] = round(json_data["bpi"]["GBP"]["rate_float"],2)
        metrics["USD"] = round(json_data["bpi"]["USD"]["rate_float"],2)

        return metrics

class OutputAllSummary(nagiosplugin.Summary):
    """Overrides normal summary object so that it changes the message summary with a custom message
       In this example, it outputs all of the metrics in one summary regardless of status"""

    @staticmethod
    def output_all_metrics(results):
        """Returns all of the metric objects in one long list"""

        output = ''

        for i in range(len(results)):
            output = output + str(results.__getitem__(i)) + ', '

        return output[:-2]

    def ok(self, results):
        return self.output_all_metrics(results)

    def problem(self, results):
        return self.output_all_metrics(results)

def get_args():
    """Parses the entered arguments and creates the help text
       Returns a parse_args object"""

    parser = argparse.ArgumentParser(description="check_bitcoin_price v1.0.0\n"
                                                  + "This plugin monitors the price of Bitcoin in different currencies.\n"
                                                  + "\nBitcoin Plugin supports the following modes:\n"
                                                  + "\nAll:    All currencies listed below"
                                                  + "\nGBP:    British Pound"
	                                              + "\nUSD:    US Dollar",formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-m", "--mode", type=str, help="Mode to monitor", required=True)
    parser.add_argument("-w", "--warning", type=str, help="Warning threshold")
    parser.add_argument("-c", "--critical", type=str, help="Critical threshold")

    try:
        args = parser.parse_args()
    except SystemExit:
        parser.exit(3)

    return args

@nagiosplugin.guarded
def main():
    """Parses the arguments, specifies the resources, contexts, metrics and summary objects to be used
       Then runs the check which will return the applicable output"""

    global args
    args = get_args()

    check = nagiosplugin.Check(
        Bitcoin(),
        nagiosplugin.ScalarContext("threshold_context", args.warning, args.critical),
        OutputAllSummary()
    )
    check.main()

if __name__ == '__main__':
    main()
