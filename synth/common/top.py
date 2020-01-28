# "TOP" means the last-known value of each property of each device.
# One use for this is so that we can set the type of each property explicitly after bulk-uploading to DevicePilot
# NOTE: Any property can occasionally have a value of None (null), from which the type can't be inferred. So we need to explicitly exclude any Nones from our "top"

class top():
    def __init__(self):
        self.top_devices = {}   # Tracks all devices and the latest value of all their properties
        self.top_properties = {}

    def update(self, new_properties):
        """ 'top' means the latest-known value of each property, for each device.
            The structure of top is:
                A set of devices
                    Each of which is a set of properties
                        Each of which is a (time, value) tuple """
        new_id = new_properties["$id"]
        new_ts = new_properties["$ts"]
        if not new_id in self.top_devices:
            self.top_devices[new_id] = {}
        existing_props = self.top_devices[new_id]
        for new_prop, new_value in new_properties.items():
            if new_prop not in existing_props:
                existing_props[new_prop] = (new_ts, new_value)
            else:
                existing_ts = existing_props[new_prop][0]
                if new_ts >= existing_ts:   # Only update if timestamp is newer
                    existing_props[new_prop] = (new_ts, new_value)

        for (k,v) in new_properties.items():    # Update top, except for null values (see NOTE above)
            if v != None:
                self.top_properties[k] = v

    def get(self):
        """Return a list of latest property-values by device""" 
        L = []            
        for dev, proptuples in self.top_devices.iteritems():
            props = {}
            for name,time_and_value in proptuples.iteritems():  # Assemble normal properties set (without times)
                props[name] = time_and_value[1]
            L.append(props)
        return L

    def get_properties(self):
        # Just the set of properties, with typical values. $id will be essentially random.
        # (from this you can deduce the type of each property)
        return self.top_properties

