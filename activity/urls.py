from rest_framework import routers

from activity.views import ActivityView
from activity.views_activity_summary import ActivitySummaryView
from activity.views_carbon_ranking import CarbonSavingRankView
from activity.views_tree import TreeActivityView
from activity.views_overall import OverallView
from activity.views_partner import PartnerView

router = routers.DefaultRouter()
router.register(r'tree-activity', TreeActivityView)
router.register(r'summary', ActivitySummaryView)
router.register(r'rank', CarbonSavingRankView)
router.register(r'overall', OverallView)
router.register(r'partner', PartnerView)
router.register(r'', ActivityView)

app_name = 'activity'
urlpatterns = router.urls
