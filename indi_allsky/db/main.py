import datetime
from pathlib import Path
#from pprint import pformat

from .models import Base
from .models import IndiAllSkyDbCameraTable
from .models import IndiAllSkyDbImageTable
from .models import IndiAllSkyDbDarkFrameTable
from .models import IndiAllSkyDbVideoTable
from .models import IndiAllSkyDbKeogramTable
from .models import IndiAllSkyDbStarTrailsTable

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

import multiprocessing

logger = multiprocessing.get_logger()


class IndiAllSkyDb(object):
    def __init__(self, config):
        self.config = config

        self._session = self._getDbConn()


    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, foobar):
        pass  # readonly


    def _getDbConn(self):

        engine = create_engine(self.config['DB_URI'], echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)

        return Session()


    def addCamera(self, camera_name):
        now = datetime.datetime.now()

        try:
            camera = self._session.query(IndiAllSkyDbCameraTable).filter(IndiAllSkyDbCameraTable.name == camera_name).one()
            camera.connectDate = now
        except NoResultFound:
            camera = IndiAllSkyDbCameraTable(
                name=camera_name,
                connectDate=now,
            )

            self._session.add(camera)

        self._session.commit()

        logger.info('Camera DB ID: %d', camera.id)

        return camera


    def addImage(self, filename, camera_id, exposure, gain, binmode, temp, adu, stable, moonmode, night=True, sqm=None, adu_roi=False, calibrated=False, stars=None):
        if not filename:
            return

        p_filename = Path(filename)
        if not p_filename.exists():
            logger.error('File not found: %s', p_filename)
            return

        logger.info('Adding image %s to DB', filename)


        filename_str = str(filename)  # might be a pathlib object


        # If temp is 0, write null
        if temp:
            temp_val = float(temp)
        else:
            temp_val = None


        # if moonmode is 0, moonphase is Null
        if moonmode:
            moonphase = float(moonmode)
        else:
            moonphase = None

        moonmode_val = bool(moonmode)

        night_val = bool(night)  # integer to boolean
        adu_roi_val = bool(adu_roi)


        if night:
            # day date for night is offset by 12 hours
            dayDate = (datetime.datetime.now() - datetime.timedelta(hours=12)).date()
        else:
            dayDate = datetime.datetime.now().date()


        image = IndiAllSkyDbImageTable(
            camera_id=camera_id,
            filename=filename_str,
            dayDate=dayDate,
            exposure=exposure,
            gain=gain,
            binmode=binmode,
            temp=temp_val,
            calibrated=calibrated,
            night=night_val,
            adu=adu,
            adu_roi=adu_roi_val,
            stable=stable,
            moonmode=moonmode_val,
            moonphase=moonphase,
            sqm=sqm,
            stars=stars,
        )

        self._session.add(image)
        self._session.commit()

        return image


    def addDarkFrame(self, filename, camera_id, bitdepth, exposure, gain, binmode, temp):
        if not filename:
            return

        #logger.info('####### Exposure: %s', pformat(exposure))

        p_filename = Path(filename)
        if not p_filename.exists():
            logger.error('File not found: %s', p_filename)
            return

        logger.info('Adding dark frame %s to DB', filename)


        filename_str = str(filename)  # might be a pathlib object

        exposure_int = int(exposure)


        # If temp is 0, write null
        if temp:
            temp_val = float(temp)
        else:
            temp_val = None


        dark = IndiAllSkyDbDarkFrameTable(
            camera_id=camera_id,
            filename=filename_str,
            bitdepth=bitdepth,
            exposure=exposure_int,
            gain=gain,
            binmode=binmode,
            temp=temp_val,
        )

        self._session.add(dark)
        self._session.commit()

        return dark


    def addVideo(self, filename, camera_id, timeofday):
        if not filename:
            return

        p_filename = Path(filename)
        if not p_filename.exists():
            logger.error('File not found: %s', p_filename)
            return

        logger.info('Adding video %s to DB', filename)


        filename_str = str(filename)  # might be a pathlib object


        if timeofday == 'night':
            night = True
        else:
            night = False


        if night:
            # day date for night is offset by 12 hours
            dayDate = (datetime.datetime.now() - datetime.timedelta(hours=12)).date()
        else:
            dayDate = datetime.datetime.now().date()


        video = IndiAllSkyDbVideoTable(
            camera_id=camera_id,
            filename=filename_str,
            dayDate=dayDate,
            night=night,
        )

        self._session.add(video)
        self._session.commit()

        return video


    def addKeogram(self, filename, camera_id, timeofday):
        if not filename:
            return

        p_filename = Path(filename)
        if not p_filename.exists():
            logger.error('File not found: %s', p_filename)
            return

        logger.info('Adding keogram %s to DB', filename)


        filename_str = str(filename)  # might be a pathlib object


        if timeofday == 'night':
            night = True
        else:
            night = False


        if night:
            # day date for night is offset by 12 hours
            dayDate = (datetime.datetime.now() - datetime.timedelta(hours=12)).date()
        else:
            dayDate = datetime.datetime.now().date()


        keogram = IndiAllSkyDbKeogramTable(
            camera_id=camera_id,
            filename=filename_str,
            dayDate=dayDate,
            night=night,
        )

        self._session.add(keogram)
        self._session.commit()

        return keogram


    def addStarTrail(self, filename, camera_id, timeofday='night'):
        if not filename:
            return

        p_filename = Path(filename)
        if not p_filename.exists():
            logger.error('File not found: %s', p_filename)
            return

        logger.info('Adding star trail %s to DB', filename)


        filename_str = str(filename)  # might be a pathlib object


        if timeofday == 'night':
            night = True
        else:
            night = False


        if night:
            # day date for night is offset by 12 hours
            dayDate = (datetime.datetime.now() - datetime.timedelta(hours=12)).date()
        else:
            dayDate = datetime.datetime.now().date()


        startrail = IndiAllSkyDbStarTrailsTable(
            camera_id=camera_id,
            filename=filename_str,
            dayDate=dayDate,
            night=night,
        )

        self._session.add(startrail)
        self._session.commit()

        return startrail




    def addUploadedFlag(self, entry):
        entry.uploaded = True
        self._session.commit()


    def getCurrentCameraId(self):
        if self.config.get('DB_CCD_ID'):
            return self.config['DB_CCD_ID']
        else:
            try:
                camera = self._session.query(IndiAllSkyDbCameraTable)\
                    .order_by(IndiAllSkyDbCameraTable.connectDate.desc())\
                    .first()
            except NoResultFound:
                logger.error('No cameras found')
                raise

        return camera.id

