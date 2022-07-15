from app.utils.string import StringUtil


class Track(object):
    def __init__(self, fm_track):
        self._set_track_values(fm_track)

    def _set_track_values(self, fm_track):
        self._name = fm_track.get('name')
        self._duration = fm_track.get('duration')
        self._location = fm_track.get('location')
        if fm_track.get('@attr') is not None:
            self._rank = fm_track.get('@attr').get('rank')
        else:
            self._rank = None
        if fm_track.get('artist') is not None:
            self._artist = fm_track.get('artist').get('name')
        else:
            self._artist = None

    @property
    def artist_name(self):
        return self._artist

    @property
    def name(self):
        return self._name

    @property
    def duration(self):
        return self._duration

    @property
    def location(self):
        return self._location

    @property
    def number(self):
        return self._rank

    def __repr__(self):
        track = dict()
        track['name'] = self.name
        track['artist_name'] = self.artist_name
        track['number'] = self.number
        track['duration'] = self.duration
        return str(track)


class TrackList(list):
    def append(self, __object: Track):
        if not isinstance(__object, Track):
            raise TypeError(f'__object is not of type {Track}')
        super(TrackList, self).append(__object)

    def lookup_track_name(self, track_name, match_ratio=100):
        for track in self:
            if StringUtil.fuzzy_match(track.name, track_name, match_ratio):
                return track
