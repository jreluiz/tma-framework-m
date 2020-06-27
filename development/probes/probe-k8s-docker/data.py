class Data:
    def __init__(self, type="measurement", descriptionId=-10, metricId=-1, observations=None):
        self.type = type
        self.descriptionID = descriptionId
        self.metricId = metricId
        if observations is None:
            observations = []
        self.observations = observations

    def add_observation(self, observation):
        self.observations.append(observation)

    def reprJSON(self):
        return dict(type=self.type, descriptionId=self.descriptionID, metricId=self.metricId, observations=self.observations)
