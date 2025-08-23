import logging
import requests
from .config import CTFD_URL, CTFD_API_KEY

logger = logging.getLogger(__name__)


class CTFdAPI:
    def __init__(self):
        self.base_url = CTFD_URL.rstrip("/")
        self.headers = {
            "Authorization": f"Token {CTFD_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        logger.info(f"CTFd API initialized for {self.base_url}")
        logger.debug(f"Using API token: {CTFD_API_KEY[:20]}...")

    def test_connection(self):
        """Test basic connectivity to CTFd instance"""
        try:
            # First test if the base URL is reachable
            resp = requests.get(self.base_url, timeout=10)
            logger.info(f"Base URL {self.base_url} returned status {resp.status_code}")

            # Test API endpoint without auth
            resp = requests.get(f"{self.base_url}/api/v1/config", timeout=10)
            logger.info(f"Config endpoint (no auth) returned status {resp.status_code}")

            # Test with auth
            resp = requests.get(
                f"{self.base_url}/api/v1/config", headers=self.headers, timeout=10
            )
            logger.info(
                f"Config endpoint (with auth) returned status {resp.status_code}"
            )

            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_top_teams(self, limit=10):
        try:
            logger.debug(f"Fetching top {limit} teams from scoreboard")
            resp = requests.get(
                f"{self.base_url}/api/v1/scoreboard", headers=self.headers
            )
            resp.raise_for_status()
            data = resp.json()
            teams = data.get("data", [])[:limit]
            logger.info(f"Successfully fetched {len(teams)} teams")
            return teams
        except Exception as e:
            logger.error(f"Error fetching top teams: {e}")
            raise

    def get_challenges(self):
        try:
            logger.debug("Fetching challenges from CTFd")
            resp = requests.get(
                f"{self.base_url}/api/v1/challenges", headers=self.headers
            )
            logger.debug(f"Response status: {resp.status_code}")
            logger.debug(f"Response headers: {dict(resp.headers)}")
            logger.debug(f"Response content (first 200 chars): {resp.text[:200]}")

            resp.raise_for_status()

            if not resp.text.strip():
                logger.error("Received empty response from CTFd API")
                return []

            try:
                challenges = resp.json().get("data", [])
                logger.debug(f"Fetched {len(challenges)} challenges")
                return challenges
            except ValueError as json_error:
                logger.error(f"Failed to parse JSON response: {json_error}")
                logger.error(f"Raw response: {resp.text}")
                return []
        except requests.exceptions.RequestException as req_error:
            logger.error(f"HTTP error fetching challenges: {req_error}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching challenges: {e}")
            raise

    def get_solves(self, challenge_id):
        try:
            logger.debug(f"Fetching solves for challenge {challenge_id}")
            resp = requests.get(
                f"{self.base_url}/api/v1/challenges/{challenge_id}/solves",
                headers=self.headers,
            )
            resp.raise_for_status()
            solves = resp.json().get("data", [])
            logger.debug(f"Found {len(solves)} solves for challenge {challenge_id}")
            return solves
        except Exception as e:
            logger.error(f"Error fetching solves for challenge {challenge_id}: {e}")
            raise

    def get_ctf_config(self):
        """Get CTF configuration using the official configs endpoint"""
        try:
            logger.debug("Fetching CTF configuration")
            resp = requests.get(f"{self.base_url}/api/v1/configs", headers=self.headers)

            if resp.status_code == 200:
                data = resp.json()
                if data.get("success") and data.get("data"):
                    logger.debug(f"Successfully fetched config")
                    return data["data"]

            logger.debug(f"Configs endpoint returned {resp.status_code}")
            return {}

        except Exception as e:
            logger.error(f"Error fetching CTF config: {e}")
            return {}

    def get_statistics_challenge_solves(self):
        """Get challenge solve statistics using the official statistics endpoint"""
        try:
            logger.debug("Fetching challenge solve statistics")
            resp = requests.get(
                f"{self.base_url}/api/v1/statistics/challenges/solves",
                headers=self.headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    logger.debug("Successfully fetched challenge solve statistics")
                    return data.get("data", {})
            logger.warning(f"Statistics endpoint returned {resp.status_code}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching challenge solve statistics: {e}")
            return {}

    def get_statistics_teams(self):
        """Get team statistics using the official statistics endpoint"""
        try:
            logger.debug("Fetching team statistics")
            resp = requests.get(
                f"{self.base_url}/api/v1/statistics/teams", headers=self.headers
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    logger.debug("Successfully fetched team statistics")
                    return data.get("data", {})
            logger.warning(f"Team statistics endpoint returned {resp.status_code}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching team statistics: {e}")
            return {}

    def get_comprehensive_statistics(self):
        """Get comprehensive statistics including solve counts and percentages"""
        try:
            stats = {}

            # Get challenge solve statistics (solve counts per challenge)
            logger.debug("Fetching comprehensive challenge statistics")
            challenge_stats = self.get_statistics_challenge_solves()
            if challenge_stats:
                stats["challenge_solves"] = challenge_stats

            # Get team statistics
            team_stats = self.get_statistics_teams()
            if team_stats:
                stats["team_stats"] = team_stats

            # Get challenge solve percentages using the /statistics/challenges endpoint
            resp = requests.get(
                f"{self.base_url}/api/v1/statistics/challenges",
                headers=self.headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    stats["challenge_percentages"] = data.get("data", {})
                    logger.debug("Successfully fetched challenge percentage statistics")
            else:
                logger.warning(
                    f"Challenge percentages endpoint returned {resp.status_code}"
                )

            # Get submission statistics
            resp = requests.get(
                f"{self.base_url}/api/v1/statistics/submissions",
                headers=self.headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    stats["submission_stats"] = data.get("data", {})
                    logger.debug("Successfully fetched submission statistics")
            else:
                logger.warning(
                    f"Submission statistics endpoint returned {resp.status_code}"
                )

            logger.info(
                f"Fetched comprehensive statistics with {len(stats)} categories"
            )
            return stats

        except Exception as e:
            logger.error(f"Error fetching comprehensive statistics: {e}")
            return {}

    def get_statistics_challenges(self):
        """Get challenge statistics including solve percentages"""
        try:
            logger.debug("Fetching challenge statistics with percentages")
            resp = requests.get(
                f"{self.base_url}/api/v1/statistics/challenges",
                headers=self.headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    logger.debug("Successfully fetched challenge statistics")
                    return data.get("data", {})
            logger.warning(f"Challenge statistics endpoint returned {resp.status_code}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching challenge statistics: {e}")
            return {}

    def get_statistics_submissions(self):
        """Get submission statistics"""
        try:
            logger.debug("Fetching submission statistics")
            resp = requests.get(
                f"{self.base_url}/api/v1/statistics/submissions",
                headers=self.headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    logger.debug("Successfully fetched submission statistics")
                    return data.get("data", {})
            logger.warning(
                f"Submission statistics endpoint returned {resp.status_code}"
            )
            return {}
        except Exception as e:
            logger.error(f"Error fetching submission statistics: {e}")
            return {}

    def get_statistics_users(self):
        """Get user statistics"""
        try:
            logger.debug("Fetching user statistics")
            resp = requests.get(
                f"{self.base_url}/api/v1/statistics/users",
                headers=self.headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    logger.debug("Successfully fetched user statistics")
                    return data.get("data", {})
            logger.warning(f"User statistics endpoint returned {resp.status_code}")
            return {}
        except Exception as e:
            logger.error(f"Error fetching user statistics: {e}")
            return {}

    def get_submissions_with_type(self, submission_type="correct"):
        """Get submissions filtered by type using the official submissions endpoint"""
        try:
            logger.debug(f"Fetching submissions with type: {submission_type}")
            params = {"type": submission_type}
            resp = requests.get(
                f"{self.base_url}/api/v1/submissions",
                headers=self.headers,
                params=params,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    submissions = data.get("data", [])
                    logger.debug(
                        f"Fetched {len(submissions)} submissions of type {submission_type}"
                    )
                    return submissions
            logger.warning(f"Submissions endpoint returned {resp.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error fetching submissions: {e}")
            return []

    def get_all_users(self):
        """Get all users/players"""
        try:
            logger.debug("Fetching all users")
            resp = requests.get(f"{self.base_url}/api/v1/users", headers=self.headers)
            resp.raise_for_status()
            users = resp.json().get("data", [])
            logger.debug(f"Fetched {len(users)} users")
            return users
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []

    def get_all_teams(self):
        """Get all teams"""
        try:
            logger.debug("Fetching all teams")
            resp = requests.get(f"{self.base_url}/api/v1/teams", headers=self.headers)
            resp.raise_for_status()
            teams = resp.json().get("data", [])
            logger.debug(f"Fetched {len(teams)} teams")
            return teams
        except Exception as e:
            logger.error(f"Error fetching teams: {e}")
            return []

    def get_all_submissions(self):
        """Get all submissions/solves"""
        try:
            logger.debug("Fetching all submissions")
            resp = requests.get(
                f"{self.base_url}/api/v1/submissions", headers=self.headers
            )
            resp.raise_for_status()
            submissions = resp.json().get("data", [])
            logger.debug(f"Fetched {len(submissions)} submissions")
            return submissions

        except Exception as e:
            logger.error(f"Error fetching submissions: {e}")
            return []
