import roslib; roslib.load_manifest('messages')
import rospy
from brass_probes.msg import Management


class ProbeState:
    NULL = 0
    INACTIVE=1
    ACTIVE=2

class ProbeLifecycle:
    CREATE=0
    ACTIVATE=1
    DEACTIVATE=2
    DESTROY=3
    CONFIGURE=4

LOCATION_SEP = '@'
NULL_LOCATION = 'NULL'

class AbstractProbe:

    _name = None
    _location = None

    def __init__(self,id,type):
        self._configParams = {}
        self.set_id(id)
        self.set_type(type)
        self._state = ProbeState.NULL

        self._management_service = rospy.Service('{}_management'.format(self.id()), ProbeManagement, self._manageProbe)
        self._reporting = rospy.Publisher('/brass/probebus',ProbeReport,queue_size=10)

    def _manageProbe(self, data):
        if (data.action == ProbeLifecycle.CREATE):
            return self.create ()
        if (data.action == ProbeLifecycle.ACTIVATE):
            return self.activate()
        if (data.action == ProbeLifecycle.DEACTIVATE):
            return self.deactivate()
        if (data.action == ProbeLifecycle.DESTROY):
            return self.destroy()
        if (data.action == ProbeLifecycle.CONFIGURE):
            return self.configure(data.config)

    def id(self):
        return '{}{}{}'.format(self._name, LOCATION_SEP, self._location)

    def name(self):
        return self._name

    def location(self):
        return self._location

    def set_id(self,id):
        if (self._name is None):
            atIdx = id.index(LOCATION_SEP)
            if (atIdx == -1):
                self._name = id
                self._location = NULL_LOCATION
            else:
                self._name = id[0:atIdx] #id.substring (0, atIdx)
                self._location = id[atIdx+1:] #id.substring(atIdx+1)

    def set_type(self, type):
        self._type = type

    def type(self):
        return self._type

    def create(self):
        if (self._state != ProbeState.NULL):
            return ProbeManagement (ProbeLifecycle.CREATE, False, 'Cannot create when probe state is {}'.format(self._state))
        self._state = ProbeState.INACTIVE
        return ProbeManagement(ProbeLifecycle.CREATE, True)

    def activate(self):
        if (self._state != ProbeState.INACTIVE):
            return ProbeManagement (ProbeLifecycle.ACTIVATE, False, 'Cannot activate when probe state is {}'.format(self._state))
        self._state = ProbeState.ACTIVE
        return ProbeManagement(ProbeLifecycle.ACTIVATE, True)

    def deactivate(self):
        if (self._state != ProbeState.ACTIVE):
            return ProbeManagement(ProbeLifecycle.DEACTIVATE, False,
                                   'Cannot deactivate when probe state is {}'.format(self._state))
        self._state = ProbeState.INACTIVE
        return ProbeManagement(ProbeLifecycle.DEACTIVATE, True)

    def destroy(self):
        if (self._state != ProbeState.INACTIVE):
            return ProbeManagement (ProbeLifecycle.DESTROY, False, 'Cannot destroy when probe state is {}'.format(self._state))
        self._state = ProbeState.NULL
        self._configParams = {}
        return ProbeManagement(ProbeLifecycle.DESTROY, True)

    def configure(self,configParams):
        self._configParams = dict(configParams)
        return ProbeManagement(ProbeLifecycle.CONFIGURE, True)

    def reportData(self,data):
        if (self._state == ProbeState.ACTIVE):
            self.reporting.publish(ProbeReport(id, type(data), str(data)))