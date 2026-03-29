'''
Preprocessor for Foliant documentation authoring tool.
Syncs issues and articles from YouTrack to markdown files.

YouTrack is a project management and issue tracking tool by JetBrains.
This preprocessor fetches issues or knowledge base articles from a
YouTrack instance via the REST API and generates markdown content
that can be included in Foliant documentation projects.
'''

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from shutil import copyfile

from foliant.preprocessors.base import BasePreprocessor


class YouTrackAPIError(Exception):
    '''Exception raised when YouTrack API returns an error.'''


class YouTrackAPI:
    '''Client for YouTrack REST API.

    Uses permanent token authentication. Obtain a token from
    YouTrack: Profile -> Hub Account -> Authentication -> New Token.
    '''

    def __init__(self, base_url: str, token: str):
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        self._base_url = base_url
        self._token = token

    def _request(self, method: str, endpoint: str, params: dict = None):
        '''Send an HTTP request to the YouTrack REST API.

        :param method: HTTP method (GET, POST, etc.)
        :param endpoint: API endpoint path (e.g. "issues")
        :param params: Query parameters dictionary

        :returns: Parsed JSON response
        '''

        url = f'{self._base_url}/api/{endpoint}'
        if params:
            query_parts = []
            for key, value in params.items():
                query_parts.append(
                    f'{urllib.parse.quote(str(key))}='
                    f'{urllib.parse.quote(str(value))}'
                )
            url += '?' + '&'.join(query_parts)

        request = urllib.request.Request(url, method=method)
        request.add_header('Authorization', f'Bearer {self._token}')
        request.add_header('Accept', 'application/json')
        request.add_header('Content-Type', 'application/json')

        try:
            with urllib.request.urlopen(request) as response:
                body = response.read().decode('utf-8')
                if body:
                    return json.loads(body)
                return {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise YouTrackAPIError(
                f'YouTrack API returned HTTP {e.code}: {error_body}'
            ) from e

    def get_issues(self, query: str = '', fields: str = None,
                   skip: int = 0, top: int = 100) -> list:
        '''Fetch a list of issues from YouTrack.

        :param query: YouTrack search query string
        :param fields: Comma-separated list of fields to return
        :param skip: Number of issues to skip (for pagination)
        :param top: Maximum number of issues to return

        :returns: List of issue dictionaries
        '''

        if fields is None:
            fields = (
                'id,idReadable,summary,description,created,updated,'
                'resolved,customFields(name,value(name,text,'
                'presentation,login,minutes,color(id)))'
            )
        params = {
            'fields': fields,
            '$skip': skip,
            '$top': top,
        }
        if query:
            params['query'] = query
        return self._request('GET', 'issues', params=params)

    def get_articles(self, query: str = '', fields: str = None,
                     skip: int = 0, top: int = 100) -> list:
        '''Fetch a list of knowledge base articles from YouTrack.

        :param query: Search query string
        :param fields: Comma-separated list of fields to return
        :param skip: Number of articles to skip (for pagination)
        :param top: Maximum number of articles to return

        :returns: List of article dictionaries
        '''

        if fields is None:
            fields = (
                'id,idReadable,summary,content,created,updated,'
                'project(name),childArticles(id,idReadable,summary)'
            )
        params = {
            'fields': fields,
            '$skip': skip,
            '$top': top,
        }
        if query:
            params['query'] = query
        return self._request('GET', 'articles', params=params)


class Preprocessor(BasePreprocessor):
    # pylint: disable=too-many-instance-attributes
    '''Preprocessor that fetches issues or articles from YouTrack
    and generates markdown content for Foliant projects.

    Config example::

        preprocessors:
          - youtrack:
              youtrack_url: https://youtrack.example.com
              youtrack_token: !env YOUTRACK_TOKEN
              project_id: MY_PROJECT
              query: 'State: Open'
              resource_type: issues
              filename: youtrack_issues.md
              format: list
              add_header: true
              header: YouTrack Issues
              add_description: true
              add_custom_fields: true
              custom_fields_filter: State, Priority, Assignee
    '''

    defaults = {
        'youtrack_url': '',
        'youtrack_token': '',
        'project_id': '',
        'query': '',
        'resource_type': 'issues',
        'fields': '',
        'filename': 'youtrack_sync.md',
        'rewrite_src_files': False,
        'max_items': 100,
        'header': 'YouTrack Issues',
        'add_header': True,
        'add_description': True,
        'add_custom_fields': True,
        'format': 'list',
        'custom_fields_filter': '',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('youtrack')

        self.logger.debug(
            'Preprocessor inited: youtrack_url=%s, project_id=%s, '
            'resource_type=%s, filename=%s',
            self.options.get('youtrack_url'),
            self.options.get('project_id'),
            self.options.get('resource_type'),
            self.options.get('filename'),
        )

        self._youtrack_url = self.options['youtrack_url']
        self._youtrack_token = self.options['youtrack_token']
        self._project_id = self.options['project_id']
        self._query = self.options['query']
        self._resource_type = self.options['resource_type']
        self._fields = self.options['fields'] or None
        self._filename = self.options['filename']
        self._rewrite_src_files = self.options['rewrite_src_files']
        self._max_items = self.options['max_items']
        self._header = self.options['header']
        self._add_header = self.options['add_header']
        self._add_description = self.options['add_description']
        self._add_custom_fields = self.options['add_custom_fields']
        self._format = self.options['format']

        self._custom_fields_filter = None
        if self.options['custom_fields_filter']:
            self._custom_fields_filter = [
                f.strip()
                for f in self.options['custom_fields_filter'].split(',')
            ]

        self._client = YouTrackAPI(self._youtrack_url, self._youtrack_token)

    def _format_custom_field_value(self, value) -> str:
        '''Extract a display string from a custom field value.

        :param value: Raw value from the YouTrack API response

        :returns: Human-readable string representation
        '''

        if value is None:
            return '\u2014'

        if isinstance(value, dict):
            return (
                value.get('name')
                or value.get('presentation')
                or value.get('text')
                or value.get('login')
                or str(value)
            )

        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, dict):
                    parts.append(
                        item.get('name')
                        or item.get('presentation')
                        or str(item)
                    )
                else:
                    parts.append(str(item))
            return ', '.join(parts) if parts else '\u2014'

        return str(value)

    def _format_custom_fields(self, custom_fields: list) -> str:
        '''Format custom fields into a markdown list.

        :param custom_fields: List of custom field dicts from the API

        :returns: Markdown-formatted custom fields string
        '''

        lines = []
        for field in custom_fields:
            name = field.get('name', '')
            if self._custom_fields_filter and name not in self._custom_fields_filter:
                continue
            display_value = self._format_custom_field_value(field.get('value'))
            lines.append(f'- **{name}**: {display_value}')

        return '\n'.join(lines)

    def _format_issue_list(self, issue: dict) -> str:
        '''Format a single issue as a markdown section.

        :param issue: Issue dict from the API

        :returns: Markdown-formatted issue string
        '''

        lines = []

        readable_id = issue.get('idReadable', issue.get('id', ''))
        summary = issue.get('summary', 'No summary')
        description = issue.get('description') or ''

        lines.append(f'### {readable_id}: {summary}\n')

        if self._add_custom_fields and 'customFields' in issue:
            cf_text = self._format_custom_fields(issue['customFields'])
            if cf_text:
                lines.append(cf_text)
                lines.append('')

        if self._add_description and description:
            lines.append(description)
            lines.append('')

        return '\n'.join(lines)

    def _build_table_header(self, sample_issue: dict) -> tuple:
        '''Build table header and separator rows from a sample issue.

        :param sample_issue: An issue dict to determine custom field columns

        :returns: Tuple of (header_row, separator_row) strings
        '''

        header = '| ID | Summary |'
        separator = '|---|---|'

        if self._add_custom_fields and 'customFields' in sample_issue:
            for field in sample_issue['customFields']:
                name = field.get('name', '')
                if self._custom_fields_filter and name not in self._custom_fields_filter:
                    continue
                header += f' {name} |'
                separator += '---|'

        return header, separator

    def _format_issue_table_row(self, issue: dict) -> str:
        '''Format a single issue as a markdown table row.

        :param issue: Issue dict from the API

        :returns: Markdown table row string
        '''

        readable_id = issue.get('idReadable', issue.get('id', ''))
        summary = issue.get('summary', 'No summary')

        # Escape pipes in summary for table compatibility
        summary = summary.replace('|', '\\|')

        row = f'| {readable_id} | {summary} |'

        if self._add_custom_fields and 'customFields' in issue:
            for field in issue['customFields']:
                name = field.get('name', '')
                if self._custom_fields_filter and name not in self._custom_fields_filter:
                    continue
                display = self._format_custom_field_value(field.get('value'))
                display = display.replace('|', '\\|')
                row += f' {display} |'

        return row

    def _format_article(self, article: dict) -> str:
        '''Format a single article as markdown.

        :param article: Article dict from the API

        :returns: Markdown-formatted article string
        '''

        lines = []

        readable_id = article.get('idReadable', article.get('id', ''))
        summary = article.get('summary', 'No summary')
        content = article.get('content') or ''

        lines.append(f'### {readable_id}: {summary}\n')

        if content:
            lines.append(content)
            lines.append('')

        child_articles = article.get('childArticles', [])
        if child_articles:
            lines.append('**Sub-articles:**\n')
            for child in child_articles:
                child_id = child.get('idReadable', child.get('id', ''))
                child_summary = child.get('summary', '')
                lines.append(f'- {child_id}: {child_summary}')
            lines.append('')

        return '\n'.join(lines)

    def _build_query(self) -> str:
        '''Build the full YouTrack search query combining project and
        user-specified filters.

        :returns: Complete query string
        '''

        query = self._query

        if self._project_id and self._resource_type == 'issues':
            project_filter = f'project: {{{self._project_id}}}'
            if query:
                query = f'{project_filter} {query}'
            else:
                query = project_filter

        return query

    def apply(self):
        '''Fetch data from YouTrack and generate markdown output.'''

        self.logger.info('Applying preprocessor')

        full_query = self._build_query()

        self.logger.debug(
            f'Fetching {self._resource_type} with query: {full_query}'
        )

        markdown_lines = []

        if self._add_header:
            markdown_lines.append(f'# {self._header}\n\n')

        if self._resource_type == 'issues':
            items = self._client.get_issues(
                query=full_query,
                fields=self._fields,
                top=self._max_items,
            )

            self.logger.debug(f'Fetched {len(items)} issues')

            if self._format == 'table':
                if items:
                    header, separator = self._build_table_header(items[0])
                    markdown_lines.append(header + '\n')
                    markdown_lines.append(separator + '\n')

                    for issue in items:
                        row = self._format_issue_table_row(issue)
                        markdown_lines.append(row + '\n')
            else:
                for issue in items:
                    text = self._format_issue_list(issue)
                    markdown_lines.append(text + '\n')

        elif self._resource_type == 'articles':
            items = self._client.get_articles(
                query=full_query,
                fields=self._fields,
                top=self._max_items,
            )

            self.logger.debug(f'Fetched {len(items)} articles')

            for article in items:
                text = self._format_article(article)
                markdown_lines.append(text + '\n')

        else:
            self.logger.error(f'Unknown resource type: {self._resource_type}')
            return

        markdown_file_path = Path(self.working_dir, self._filename)
        markdown_file_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger.debug(f'Writing to: {markdown_file_path}')

        with open(markdown_file_path, 'w', encoding='utf-8') as f:
            for line in markdown_lines:
                f.write(line)

        if self._rewrite_src_files:
            src_file_path = Path(
                self.project_path, self.config['src_dir'], self._filename
            )
            src_file_path.parent.mkdir(parents=True, exist_ok=True)
            copyfile(markdown_file_path, src_file_path)

        self.logger.info('Preprocessor applied')
