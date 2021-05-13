def create_labels():
    file = open("component6/grammar/obligations.txt").read().split("\n")
    sentiments = ["positive", "negative", "neutral"]
    subjectivities = ["subjective", "objective"]
    outfile = open("component6/grammar/labels.txt", "w")
    for line in file:
        label = line.split(":")[0]
        for sentiment in sentiments:
            for subjectivity in subjectivities:
                new_label = f"{label}-{sentiment}-{subjectivity} ->"
                outfile.write(new_label+"\n")


if __name__ == "__main__":
    create_labels()