import json
from config.models import Config
from config.serializers import ConfigSerializer


# If edit this file please update file /config_scss/_data/sass.tar.gz
def generate_color():
    _ = Config.pull_value('config-menu-text-color')
    if _ == '#######':
        Config.set_value('config-menu-text-color', '#231F20')

    return """$primary-color: %s;
$secondary-color: %s;
$black-color: %s;
$yellow-color: %s;
$red-color: %s;
$blue-color: %s;
$green-color: %s;

$header-bg-color: %s;
$header-text-color: %s;
$heading-color: %s;
$title-color: %s;
$description-color: %s;
$notification-color: %s;
$information-color: %s;

$login-text-color: %s;
$login-button-color: %s;
$login-button-text-color: %s;

$progress-not-start-color: %s;
$progress-in-progress-color: %s;
$progress-verifying-color: %s;
$progress-completed-color: %s;
$progress-failed-color: %s;
$progress-canceled-color: %s;
$progress-rejected-color: %s;
$progress-expired-color: %s;
$progress-waiting-list-color: %s;
$progress-waiting-approve-color: %s;
$progress-waiting-form-color: %s;
$progress-re-submit-color: %s;

$label-new-color: %s;
$label-upcoming-color: %s;
$label-open-to-enroll-color: %s;
$label-end-to-enroll-color: %s;
$label-ongoing-color: %s;
$label-enrolled-color: %s;
$label-assigned-color: %s;
$label-ended-color: %s;
$label-canceled-color: %s;
$label-full-color: %s;

$button-enroll-color: %s;
$button-disable-color: %s;
$button-full-color: %s;
$button-waiting-color: %s;

$content-course-color: %s;
$content-event-color: %s;
$content-survey-color: %s;
$content-exam-color: %s;
$content-activity-color: %s;
$content-onboard-color: %s;
$content-program-color: %s;
$content-learning-path-color: %s;
$content-public-learning-color: %s;
$content-live-color: %s;
$content-material-video-color: %s;
$content-material-audio-color: %s;

$menu-bg-color: %s;
$menu-text-color: %s;
$menu-text-selected-color: %s;
$menu-icon-color: %s;
$menu-icon-selected-color: %s;
$bg-color: %s;
            """ % (
        Config.pull_value('config-primary-color', is_force=True),
        Config.pull_value('config-secondary-color', is_force=True),
        Config.pull_value('config-black-color', is_force=True),
        Config.pull_value('config-yellow-color', is_force=True),
        Config.pull_value('config-red-color', is_force=True),
        Config.pull_value('config-blue-color', is_force=True),
        Config.pull_value('config-green-color', is_force=True),

        Config.pull_value('config-header-background-color', is_force=True),
        Config.pull_value('config-header-text-color', is_force=True),
        Config.pull_value('config-heading-color', is_force=True),
        Config.pull_value('config-title-color', is_force=True),
        Config.pull_value('config-description-color', is_force=True),
        Config.pull_value('config-notification-color', is_force=True),
        Config.pull_value('config-information-color', is_force=True),

        Config.pull_value('config-login-text-color', is_force=True),
        Config.pull_value('config-login-button-color', is_force=True),
        Config.pull_value('config-login-button-text-color', is_force=True),

        Config.pull_value('config-progress-not-start-color', is_force=True),
        Config.pull_value('config-progress-in-progress-color', is_force=True),
        Config.pull_value('config-progress-verifying-color', is_force=True),
        Config.pull_value('config-progress-completed-color', is_force=True),
        Config.pull_value('config-progress-failed-color', is_force=True),
        Config.pull_value('config-progress-canceled-color', is_force=True),
        Config.pull_value('config-progress-rejected-color', is_force=True),
        Config.pull_value('config-progress-expired-color', is_force=True),
        Config.pull_value('config-progress-waiting-list-color', is_force=True),
        Config.pull_value('config-progress-waiting-approve-color', is_force=True),
        Config.pull_value('config-progress-waiting-form-color', is_force=True),
        Config.pull_value('config-progress-re-submit-color', is_force=True),

        Config.pull_value('config-label-new-color', is_force=True),
        Config.pull_value('config-label-upcoming-color', is_force=True),
        Config.pull_value('config-label-open-to-enroll-color', is_force=True),
        Config.pull_value('config-label-end-to-enroll-color', is_force=True),
        Config.pull_value('config-label-ongoing-color', is_force=True),
        Config.pull_value('config-label-enrolled-color', is_force=True),
        Config.pull_value('config-label-assigned-color', is_force=True),
        Config.pull_value('config-label-ended-color', is_force=True),
        Config.pull_value('config-label-canceled-color', is_force=True),
        Config.pull_value('config-label-full-color', is_force=True),

        Config.pull_value('config-button-enroll-color', is_force=True),
        Config.pull_value('config-button-disable-color', is_force=True),
        Config.pull_value('config-button-full-color', is_force=True),
        Config.pull_value('config-button-waiting-color', is_force=True),

        Config.pull_value('content-course-color', is_force=True),
        Config.pull_value('content-event-color', is_force=True),
        Config.pull_value('content-survey-color', is_force=True),
        Config.pull_value('content-exam-color', is_force=True),
        Config.pull_value('content-activity-color', is_force=True),
        Config.pull_value('content-onboard-color', is_force=True),
        Config.pull_value('content-program-color', is_force=True),
        Config.pull_value('content-learning-path-color', is_force=True),
        Config.pull_value('content-public-learning-color', is_force=True),
        Config.pull_value('content-live-color', is_force=True),
        Config.pull_value('content-material-video-color', is_force=True),
        Config.pull_value('content-material-audio-color', is_force=True),

        Config.pull_value('config-menu-background-color', is_force=True),
        Config.pull_value('config-menu-text-color', is_force=True),
        Config.pull_value('config-menu-text-selected-color', is_force=True),
        Config.pull_value('config-menu-icon-color', is_force=True),
        Config.pull_value('config-menu-icon-selected-color', is_force=True),
        Config.pull_value('config-background-color', is_force=True),
    )


def generate_config_file():
    config_code_list = ['meta-description', 'og-title', 'og-description', 'og-image', 'config-app-name']
    config_list = Config.objects.filter(code__in=config_code_list)
    response = {}
    for config in config_list:
        response.update({
            config.code: ConfigSerializer(config).data
        })
    return json.dumps(response)
