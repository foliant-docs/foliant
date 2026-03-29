'''Test the YouTrack preprocessor that syncs issues and articles
from YouTrack to markdown files.
'''

import json
from logging import Logger
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from foliant.preprocessors.youtrack import (
    Preprocessor,
    YouTrackAPI,
    YouTrackAPIError,
)


SAMPLE_ISSUES = [
    {
        'id': '2-1',
        'idReadable': 'PRJ-1',
        'summary': 'First issue',
        'description': 'Description of the first issue.',
        'customFields': [
            {'name': 'State', 'value': {'name': 'Open'}},
            {'name': 'Priority', 'value': {'name': 'Critical'}},
            {'name': 'Assignee', 'value': {'login': 'admin', 'name': 'Admin User'}},
        ],
    },
    {
        'id': '2-2',
        'idReadable': 'PRJ-2',
        'summary': 'Second issue',
        'description': None,
        'customFields': [
            {'name': 'State', 'value': {'name': 'In Progress'}},
            {'name': 'Priority', 'value': {'name': 'Normal'}},
            {'name': 'Assignee', 'value': None},
        ],
    },
]

SAMPLE_ARTICLES = [
    {
        'id': '3-1',
        'idReadable': 'A-PRJ-1',
        'summary': 'Getting Started',
        'content': 'Welcome to the project.',
        'childArticles': [
            {'id': '3-2', 'idReadable': 'A-PRJ-2', 'summary': 'Installation'},
        ],
    },
]


class TestYouTrackAPI:
    def test_init_strips_trailing_slash(self):
        api = YouTrackAPI('https://youtrack.example.com/', 'test-token')
        assert api._base_url == 'https://youtrack.example.com'

    def test_init_no_trailing_slash(self):
        api = YouTrackAPI('https://youtrack.example.com', 'test-token')
        assert api._base_url == 'https://youtrack.example.com'


class TestPreprocessorFormatting:
    '''Test formatting methods of the preprocessor without API calls.'''

    @pytest.fixture
    def preprocessor(self, tmp_path):
        context = {
            'project_path': tmp_path,
            'config': {'tmp_dir': Path('__folianttmp__')},
        }
        options = {
            'youtrack_url': 'https://youtrack.example.com',
            'youtrack_token': 'test-token',
            'project_id': 'PRJ',
        }
        return Preprocessor(context, Logger('test'), options=options)

    def test_format_custom_field_value_none(self, preprocessor):
        assert preprocessor._format_custom_field_value(None) == '\u2014'

    def test_format_custom_field_value_dict_name(self, preprocessor):
        assert preprocessor._format_custom_field_value({'name': 'Open'}) == 'Open'

    def test_format_custom_field_value_dict_presentation(self, preprocessor):
        assert preprocessor._format_custom_field_value(
            {'presentation': '2h 30m'}
        ) == '2h 30m'

    def test_format_custom_field_value_dict_login(self, preprocessor):
        assert preprocessor._format_custom_field_value(
            {'login': 'admin'}
        ) == 'admin'

    def test_format_custom_field_value_list(self, preprocessor):
        result = preprocessor._format_custom_field_value([
            {'name': 'Tag1'},
            {'name': 'Tag2'},
        ])
        assert result == 'Tag1, Tag2'

    def test_format_custom_field_value_empty_list(self, preprocessor):
        assert preprocessor._format_custom_field_value([]) == '\u2014'

    def test_format_custom_field_value_string(self, preprocessor):
        assert preprocessor._format_custom_field_value('some text') == 'some text'

    def test_format_custom_field_value_int(self, preprocessor):
        assert preprocessor._format_custom_field_value(42) == '42'

    def test_format_custom_fields(self, preprocessor):
        fields = [
            {'name': 'State', 'value': {'name': 'Open'}},
            {'name': 'Priority', 'value': {'name': 'Critical'}},
        ]
        result = preprocessor._format_custom_fields(fields)
        assert '- **State**: Open' in result
        assert '- **Priority**: Critical' in result

    def test_format_custom_fields_with_filter(self, tmp_path):
        context = {
            'project_path': tmp_path,
            'config': {'tmp_dir': Path('__folianttmp__')},
        }
        options = {
            'youtrack_url': 'https://youtrack.example.com',
            'youtrack_token': 'test-token',
            'project_id': 'PRJ',
            'custom_fields_filter': 'State',
        }
        prep = Preprocessor(context, Logger('test'), options=options)
        fields = [
            {'name': 'State', 'value': {'name': 'Open'}},
            {'name': 'Priority', 'value': {'name': 'Critical'}},
        ]
        result = prep._format_custom_fields(fields)
        assert '- **State**: Open' in result
        assert 'Priority' not in result

    def test_format_issue_list(self, preprocessor):
        issue = SAMPLE_ISSUES[0]
        result = preprocessor._format_issue_list(issue)
        assert '### PRJ-1: First issue' in result
        assert 'Description of the first issue.' in result
        assert '- **State**: Open' in result

    def test_format_issue_list_no_description(self, preprocessor):
        issue = SAMPLE_ISSUES[1]
        result = preprocessor._format_issue_list(issue)
        assert '### PRJ-2: Second issue' in result
        assert 'Description' not in result.split('\n', 1)[-1]

    def test_format_issue_table_row(self, preprocessor):
        issue = SAMPLE_ISSUES[0]
        result = preprocessor._format_issue_table_row(issue)
        assert result.startswith('| PRJ-1 | First issue |')
        assert 'Open' in result
        assert 'Critical' in result

    def test_format_issue_table_row_escapes_pipes(self, preprocessor):
        issue = {
            'id': '2-3',
            'idReadable': 'PRJ-3',
            'summary': 'Issue with | pipe',
            'customFields': [],
        }
        result = preprocessor._format_issue_table_row(issue)
        assert 'Issue with \\| pipe' in result

    def test_build_table_header(self, preprocessor):
        header, separator = preprocessor._build_table_header(SAMPLE_ISSUES[0])
        assert '| ID | Summary |' in header
        assert 'State' in header
        assert 'Priority' in header
        assert separator.count('---|') >= 2

    def test_format_article(self, preprocessor):
        article = SAMPLE_ARTICLES[0]
        result = preprocessor._format_article(article)
        assert '### A-PRJ-1: Getting Started' in result
        assert 'Welcome to the project.' in result
        assert 'A-PRJ-2: Installation' in result

    def test_format_article_no_content(self, preprocessor):
        article = {
            'id': '3-3',
            'idReadable': 'A-PRJ-3',
            'summary': 'Empty article',
            'content': None,
            'childArticles': [],
        }
        result = preprocessor._format_article(article)
        assert '### A-PRJ-3: Empty article' in result

    def test_build_query_with_project_and_user_query(self, preprocessor):
        preprocessor._query = 'State: Open'
        preprocessor._project_id = 'PRJ'
        preprocessor._resource_type = 'issues'
        result = preprocessor._build_query()
        assert 'project: {PRJ}' in result
        assert 'State: Open' in result

    def test_build_query_project_only(self, preprocessor):
        preprocessor._query = ''
        preprocessor._project_id = 'PRJ'
        preprocessor._resource_type = 'issues'
        result = preprocessor._build_query()
        assert result == 'project: {PRJ}'

    def test_build_query_articles_no_project_filter(self, preprocessor):
        preprocessor._query = 'some query'
        preprocessor._project_id = 'PRJ'
        preprocessor._resource_type = 'articles'
        result = preprocessor._build_query()
        assert result == 'some query'
        assert 'project' not in result


class TestPreprocessorApply:
    '''Test the apply method with mocked API calls.'''

    @pytest.fixture
    def tmp_project(self, tmp_path):
        working_dir = tmp_path / '__folianttmp__'
        working_dir.mkdir()
        return tmp_path

    def _make_preprocessor(self, tmp_project, **extra_options):
        context = {
            'project_path': tmp_project,
            'config': {'tmp_dir': Path('__folianttmp__')},
        }
        options = {
            'youtrack_url': 'https://youtrack.example.com',
            'youtrack_token': 'test-token',
            'project_id': 'PRJ',
            **extra_options,
        }
        return Preprocessor(context, Logger('test'), options=options)

    @patch.object(YouTrackAPI, 'get_issues', return_value=SAMPLE_ISSUES)
    def test_apply_issues_list_format(self, mock_get, tmp_project):
        prep = self._make_preprocessor(tmp_project, format='list')
        prep.apply()

        output_path = tmp_project / '__folianttmp__' / 'youtrack_sync.md'
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert '# YouTrack Issues' in content
        assert '### PRJ-1: First issue' in content
        assert '### PRJ-2: Second issue' in content

    @patch.object(YouTrackAPI, 'get_issues', return_value=SAMPLE_ISSUES)
    def test_apply_issues_table_format(self, mock_get, tmp_project):
        prep = self._make_preprocessor(tmp_project, format='table')
        prep.apply()

        output_path = tmp_project / '__folianttmp__' / 'youtrack_sync.md'
        content = output_path.read_text(encoding='utf-8')
        assert '| ID | Summary |' in content
        assert '| PRJ-1 | First issue |' in content

    @patch.object(YouTrackAPI, 'get_articles', return_value=SAMPLE_ARTICLES)
    def test_apply_articles(self, mock_get, tmp_project):
        prep = self._make_preprocessor(
            tmp_project, resource_type='articles', header='Knowledge Base'
        )
        prep.apply()

        output_path = tmp_project / '__folianttmp__' / 'youtrack_sync.md'
        content = output_path.read_text(encoding='utf-8')
        assert '# Knowledge Base' in content
        assert '### A-PRJ-1: Getting Started' in content

    @patch.object(YouTrackAPI, 'get_issues', return_value=[])
    def test_apply_no_header(self, mock_get, tmp_project):
        prep = self._make_preprocessor(tmp_project, add_header=False)
        prep.apply()

        output_path = tmp_project / '__folianttmp__' / 'youtrack_sync.md'
        content = output_path.read_text(encoding='utf-8')
        assert '# YouTrack Issues' not in content

    @patch.object(YouTrackAPI, 'get_issues', return_value=SAMPLE_ISSUES)
    def test_apply_custom_filename(self, mock_get, tmp_project):
        prep = self._make_preprocessor(tmp_project, filename='my_issues.md')
        prep.apply()

        output_path = tmp_project / '__folianttmp__' / 'my_issues.md'
        assert output_path.exists()

    @patch.object(YouTrackAPI, 'get_issues', return_value=SAMPLE_ISSUES)
    def test_apply_rewrite_src_files(self, mock_get, tmp_project):
        src_dir = tmp_project / 'src'
        src_dir.mkdir()
        context = {
            'project_path': tmp_project,
            'config': {
                'tmp_dir': Path('__folianttmp__'),
                'src_dir': 'src',
            },
        }
        options = {
            'youtrack_url': 'https://youtrack.example.com',
            'youtrack_token': 'test-token',
            'project_id': 'PRJ',
            'rewrite_src_files': True,
        }
        prep = Preprocessor(context, Logger('test'), options=options)
        prep.apply()

        src_file = tmp_project / 'src' / 'youtrack_sync.md'
        assert src_file.exists()

    def test_apply_unknown_resource_type(self, tmp_project):
        prep = self._make_preprocessor(tmp_project, resource_type='unknown')
        # Should not raise, just log error and return
        prep.apply()
        output_path = tmp_project / '__folianttmp__' / 'youtrack_sync.md'
        assert not output_path.exists()
