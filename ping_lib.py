from platform import system as system_name # Returns the system/OS name
import subprocess


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that some hosts may not respond to a ping request even if the host name is valid.
    """

    # Ping parameters as function of OS
    parameters = "-n 1" if system_name().lower() == "windows" else "-c 1"

    # Pinging
    return subprocess.call("ping " + parameters + " " + host, shell=False)
