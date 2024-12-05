import pandas as pd
from typing import List, Optional, Dict
from datetime import datetime
from const import REQUIRED_SAMPLES
from collections import defaultdict

class Sample:
    def __init__(self, month: datetime.date, group: int, rnpd: float, duration: int):
        self.month = month
        self.group = group # ranging between 1-12 possible groups(M)
        self.rnpd = rnpd  #  rnpd calculated before in the pipeline
        self.duration = duration  # rounded value of DurationBruto


class Duration:
    def __init__(self, group:int, duration: int, samples: List[Sample]):
        self.group = group
        self.duration = duration
        self.samples = []
        self.update_multiple_items(samples)

    def update_one_item(self, sample: Sample):
        if len(self.samples) < REQUIRED_SAMPLES[self.group]:
            self.samples.append(sample)
        else:
            # find the oldest sample in group/duration and replace it:
            oldest_sample: Optional[Sample] = None
            for s in self.samples:
                if oldest_sample is None or s.month < oldest_sample.month:
                    oldest_sample = s
            self.samples.remove(oldest_sample)
            self.samples.append(sample)

    def update_multiple_items(self, samples: List[Sample]):
        for sam in samples:
            # check subsample belongs to correct group and duration before adding
            if sam.group == self.group and sam.duration == self.duration:
                self.update_one_item(sam)

    def get_list_len(self):
        return len(self.samples)


class M:
    def __init__(self, group: int):
        self.group = group
        self.durations: Optional[dict[int, Duration]] = {}

    def update_items(self, data: pd.DataFrame):
        # Filter rows where column M matches the current group.
        df = data[data['M'] == self.group].copy()

        # Group the DataFrame by duration (x) and create Sample objects for each group.
        samples = df.groupby('Duration').apply(
                        lambda group: [Sample(row['month'], row['M'], row['Rnpd'], row['Duration'])
                        for index, row in group.iterrows()])
        # Iterate over unique durations in the DataFrame.
        for dur in sorted(df['Duration'].unique()):
            # Initialize durations dictionary if empty.
            if not dur in self.durations.keys():
                self.durations[dur] = Duration(self.group, dur, samples.loc[dur])
            else:
                self.durations[dur].update_multiple_items(samples.loc[dur])
