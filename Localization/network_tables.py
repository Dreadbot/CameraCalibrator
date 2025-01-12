import ntcore
from poseclass import Position

def start_network_table():
    inst = ntcore.NetworkTableInstance.getDefault()
    table = inst.getTable("azathoth")
    inst.startClient4("visionclient")
    inst.setServerTeam(3656)
    positionPub = table.getStructArrayTopic("visionPos", Position).publish()
    latencyPub = table.getDoubleTopic("visionLatency").publish()
    tagSeenPub = table.getBooleanTopic("tagSeen").publish()
    return tagSeenPub, latencyPub, positionPub
