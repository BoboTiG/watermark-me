"""
GUI to watermark your pictures with text and/or another picture.

This module is maintained by Mickaël Schoentgen <contact@tiger-222.fr>.

You can always get the latest version of this module at:
    https://github.com/BoboTiG/watermark-me
If that URL should fail, try contacting the author.
"""
import logging
import subprocess

from PyQt5.QtWidgets import qApp

from .base import BaseUpdater


class Updater(BaseUpdater):
    """ Windows updater. """

    def install(self, filename: str) -> None:
        """
        The installer will automagically:
            - try to stop the application, if not already done
            - install the new version
            - start the new version

        So, a big thank you to Inno Setup!
        """

        # Using ping instead of timeout to wait 5 seconds
        cmd = f'ping 127.0.0.1 -n 6 > nul && "{filename}" /verysilent /start=auto'
        logging.info("Launching the auto-updater in 5 seconds ...")
        subprocess.Popen(cmd, shell=True, close_fds=True)

        # Exit the the app
        qApp.quit()
