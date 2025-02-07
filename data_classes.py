import pandas as pd
from typing import List, Optional, Dict
from datetime import datetime
from const import REQUIRED_SAMPLES


class Sample:
    def __init__(self, month: datetime.date, group: int, rnpd: float, duration: int):
        self.month = month
        self.group = group # ranging between 1-12 possible groups(M)
        self.rnpd = rnpd  #  rnpd calculated before in the pipeline
        self.duration = duration  # rounded monthly value of DurationBruto


class Duration:
    def __init__(self, group:int, duration: int, samples: List[Sample]):
        self.group = group
        self.duration = duration
        self.samples = []
        self.set_multiple_samples(samples)

    def get_oldest_sample(self) -> Optional[Sample]:
        return min(self.samples, key=lambda sample: sample.month) if self.samples else None

    def set_new_sample(self, sample: Sample):
        if len(self.samples) < REQUIRED_SAMPLES[self.group]:
            self.samples.append(sample)
        else:
            oldest_sample : Optional[Sample] = self.get_oldest_sample()
            self.samples.remove(oldest_sample)
            self.samples.append(sample)

    def set_multiple_samples(self, samples: List[Sample]):
        for sam in samples:
            if sam.group == self.group and sam.duration == self.duration:
                self.set_new_sample(sam)

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
        if not df.empty:
            for duration_index in sorted(df['Duration'].unique()):
                if not duration_index in self.durations.keys():
                    self.durations[duration_index] = Duration(self.group, duration_index, samples.loc[duration_index])
                else:
                    self.durations[duration_index].set_multiple_samples(samples.loc[duration_index])
