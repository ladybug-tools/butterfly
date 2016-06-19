# OpenFoam Fields
class BoundaryField:
    """OpenFoam Boundary Field

    Attributes:
        name    : Name of boundary field as a string
        bcType  : Type of boundary field (e.g fixedFluxPressure)
        value   : Value as a string (e.g uniform (0 0 0), )
        other   : A dictionary of other optional fields as key, values

    Usage:
        # create boundary field
        floor_bof = BoundaryField(name = "floor",
            bfType = "alphatJayatillekeWallFunction",
            value = "uniform 0")

        # add a new field
        floor_bof.add_properties(properties={"Prt" : "0.85"})
        print "Property is added > " + str(bof.properties)

        # update the value for
        floor_bof.update_properties(properties={"Prt" : "0.80", "notValid" : "0"})
        print "Value is updated to 0.80 > " + str(bof.properties)

        # remove Prt
        floor_bof.remove_property("Prt")
        print "Prt is removed > " + str(bof.properties)

        # get OpenFoam string
        print "This is how it will be in OpenFoam File >\n" + floor_bof.get_OFString()

        # add another boundary field
        fixedWalls_bof = BoundaryField(name = "fixedWalls",
            bfType = "alphatJayatillekeWallFunction",
            value = "uniform 0",
            other = {"prt":"0.85"})

        # get full string
        print BoundaryField.get_BoundaryFieldsOFString([floor_bof, fixedWalls_bof])
    """

    #TODO: Value should be it's own object but I don't really know all the value
    #      types to write it. Let me (=@mostaphsRoudsari) know if you can help here.
    def __init__(self, name, bfType, value = None, other = {}):
        self.__properties = {}
        self.name = str(name)
        self.__properties["type"] = str(bfType)
        # value is optional but very common
        if value != None:
            self.__properties["value"] = str(value)
        for key, value in other.items():
            self.properties[str(key)] = str(str(value))

    @property
    def properties(self):
        return self.__properties

    def add_properties(self, properties = {}):
        """Add new properties to boundary field"""
        props = self.__properties.keys()
        newProps = properties.keys()
        for key in newProps:
            if key not in props:
                self.properties[str(key)] = str(properties[key])
            else:
                print "%s is already set. Use update_properties to update the value"%key

    def update_properties(self, properties = {}):
        """Update values of multiple properties"""
        props = self.__properties.keys()
        propsToUpdate = properties.keys()
        for key in propsToUpdate:
            if key in props:
                self.properties[str(key)] = str(properties[key])
            else:
                print "%s is not a property. Use add_properties to update the value"%key

    def remove_property(self, propertyName):
        """Remove one of the properties"""
        try:
            del(self.__properties[propertyName])
            return True
        except:
            print "Failed to remove %s"%propertyName
            return False

    def get_OFString(self):
        """Return open foam style string"""
        props = ["\t\t" + key + "\t\t\t" + value + ";" for key, value in self.__properties.items()]

        return  "\t" + self.name + "\n\t{\n" + \
                "\n".join(props) + \
                "\n\t}\n"

    @staticmethod
    def get_BoundaryFieldsOFString(boundaryFields):
        bfs = []
        for bf in boundaryFields:
            if isinstance(bf, BoundaryField):
                bfs.append(bf.get_OFString())
            else:
                raise TypeError("%s is not a BoundaryField!" )

        return "boundaryField\n{\n" + \
                "".join(bfs) + \
                "}\n"

    def __repr__(self):
        return self.name


class InternalField:
    """OpenFoam Internal Field

        Attributes:
            value   : Value as a string (e.g uniform 0)

        Usage:
            iff = InternalField("uniform 0")
            print iff.value
            print iff.get_OFString()
    """

    #TODO: Value should be it's own object but I don't really know all the value
    #      types to write it. Let me (=@mostaphsRoudsari) know if you can help here.
    def __init__(self, value):
        self.__value = str(value)

    def update_value(self, newValue):
        """Update value"""
        self.__value = str(newValue)

    @property
    def value(self):
        return self.__value

    def get_OFString(self):
        """Return open foam style string"""
        return  "internalField\t" + self.value + ";\n"


class Dimensions:
    """OpenFoam Dimensional Units

        Each of the values corresponds to the power of each of
        the base units of measurement.

        Read section 4.2.6 at this link:
        http://cfd.direct/openfoam/user-guide/basic-file-format/

        Attributes:
            mass        :   kilogram (kg) | pound-mass (lbm) (default = 0)
            length      :   metre (m) | foot (ft) (default = 0)
            time        :   seconds (s) (default = 0)
            temperature :   Kelvin (K) | degree Rankine (R) (default = 0)
            quantity    :   mole (mol) (default = 0)
            current     :   ampere (A) (default = 0)
            luminousIntensity : candela (cd) (default = 0)

        Usage:
            dm = Dimensions(0, 2, -1, 0, 0 ,0, 0)
            dm.update_timeValue(-2)
            print dm.get_OFString()
    """

    def __init__(self, mass = 0, length = 0, time = 0, temperature = 0,
        quantity = 0, current = 0, luminousIntensity = 0):
        self.__mass = int(mass)
        self.__length = int(length)
        self.__time = int(time)
        self.__temperature = int(temperature)
        self.__quantity = int(quantity)
        self.__current = int(current)
        self.__luminousIntensity = int(luminousIntensity)

    def update(self, mass, length, time, temperature,
        quantity, current, luminousIntensity):
        """Update all values"""
        self.__mass = int(mass)
        self.__length = int(length)
        self.__time = int(time)
        self.__temperature = int(temperature)
        self.__quantity = int(quantity)
        self.__current = int(current)
        self.__luminousIntensity = int(luminousIntensity)

    def update_massValue(self, newValue):
        """Update value for mass"""
        self.__mass = int(newValue)

    def update_lengthValue(self, newValue):
        """Update value for length"""
        self.__length = int(newValue)

    def update_timeValue(self, newValue):
        """Update value for time"""
        self.__time = int(newValue)

    def update_temperatureValue(self, newValue):
        """Update value for temperature"""
        self.__temperature = int(newValue)

    def update_quantityValue(self, newValue):
        """Update value for quantity"""
        self.__quantity = int(newValue)

    def update_currentValue(self, newValue):
        """Update value for current"""
        self.__current = int(newValue)

    def update_luminousIntensityValue(self, newValue):
        """Update value for luminousIntensity"""
        self.__luminousIntensity = int(newValue)

    def get_values(self):
        values = [self.__mass, self.__length, self.__time, self.__temperature, \
            self.__quantity, self.__current, self.__luminousIntensity]

        return "[%s]"%", ".join(map(str, values))

    def get_OFString(self):
        """Return open foam style string"""
        return  "dimensions\t" + self.get_values() + ";\n"

    def __repr__(self):
        return self.get_values()
