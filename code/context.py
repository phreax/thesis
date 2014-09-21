class ContextAbstractor:

    weekend = [5,6]
    dayhours = [0,6,12,18]

    def __init__(self, use_tod=True, use_dow=True):
        self.use_tod = use_tod
        self.use_dow = use_dow

        self.dayperiods = list(enumerate(zip(self.dayhours[::1],self.dayhours[1::])))

    def retrieve_context(self, t):
        dayofweek = 0
        timeofday = 0

        if t.weekday() in self.weekend:
            dayofweek = 1

        hour = t.hour
        for i,(t1,t2) in self.dayperiods:
            if hour >= t1 and hour < t2:
                timeofday = i+1
                break

        return self.encode_context(dayofweek,timeofday)

    def encode_context(self,dow,tod):
        if self.use_tod and self.use_dow:
            return tod + (self.dim_tod*dow)
        if self.use_tod:
            return tod
        if self.use_dow:
            return dow
        return 0

    @property
    def dim_dow(self):
        return 2

    @property
    def dim_tod(self):
        return len(self.dayperiods)+1

    @property
    def dim(self):
        if self.use_tod and self.use_dow:
            return self.dim_dow*self.dim_tod
        if self.use_tod:
            return self.dim_tod
        if self.use_dow:
            return self.dim_dow
        return 1

    def values(self):
        '''Iterate over all context values'''
        return xrange(self.dim)
