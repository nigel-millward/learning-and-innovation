"""Tests for cleaning Confluence storage-format XHTML into plain text."""

from confluence_indexer.processing.cleaning import StorageFormatCleaner

clean = StorageFormatCleaner().clean


def test_headings_paragraphs_and_inline_markup():
    text = clean("<h1>Deploying</h1><p>Run <strong>make</strong> then <em>wait</em>.</p>")
    assert text == "# Deploying\n\nRun make then wait."


def test_navigation_macros_are_removed():
    storage = (
        '<ac:structured-macro ac:name="toc"><ac:parameter ac:name="maxLevel">3</ac:parameter>'
        "</ac:structured-macro>"
        '<ac:structured-macro ac:name="children"/>'
        '<ac:structured-macro ac:name="excerpt-include">'
        '<ac:parameter ac:name="">Other page</ac:parameter></ac:structured-macro>'
        "<p>Real content.</p>"
    )
    assert clean(storage) == "Real content."


def test_panel_macros_keep_their_body_and_title():
    storage = (
        '<ac:structured-macro ac:name="warning">'
        '<ac:parameter ac:name="title">Careful</ac:parameter>'
        "<ac:rich-text-body><p>Do not restart prod on Fridays.</p></ac:rich-text-body>"
        "</ac:structured-macro>"
    )
    assert clean(storage) == "Careful\n\nDo not restart prod on Fridays."


def test_code_macro_is_fenced_and_preserves_layout():
    storage = (
        '<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">bash</ac:parameter>'
        "<ac:plain-text-body><![CDATA[if [ -f x ]; then\n  echo <ok>\n\n  exit 0\nfi]]>"
        "</ac:plain-text-body></ac:structured-macro>"
    )
    assert clean(storage) == "```\nif [ -f x ]; then\n  echo <ok>\n\n  exit 0\nfi\n```"


def test_links_render_as_their_text():
    storage = (
        '<p>See <ac:link><ri:page ri:content-title="Runbook"/></ac:link> and '
        '<ac:link><ri:page ri:content-title="X"/><ac:plain-text-link-body><![CDATA[the docs]]>'
        "</ac:plain-text-link-body></ac:link>.</p>"
    )
    assert clean(storage) == "See Runbook and the docs."


def test_tables_become_pipe_rows():
    storage = (
        "<table><tbody><tr><th>Env</th><th>URL</th></tr>"
        "<tr><td><p>prod</p></td><td>https://example.com</td></tr></tbody></table>"
    )
    assert clean(storage) == "Env | URL\nprod | https://example.com"


def test_nested_lists_keep_indentation():
    storage = "<ul><li>One<ul><li>One.a</li></ul></li><li>Two</li></ul><ol><li>First</li></ol>"
    assert clean(storage) == "- One\n  - One.a\n- Two\n\n1. First"


def test_task_lists():
    storage = (
        "<ac:task-list><ac:task><ac:task-status>complete</ac:task-status>"
        "<ac:task-body>Write tests</ac:task-body></ac:task>"
        "<ac:task><ac:task-status>incomplete</ac:task-status>"
        "<ac:task-body>Ship it</ac:task-body></ac:task></ac:task-list>"
    )
    assert clean(storage) == "- [x] Write tests\n- [ ] Ship it"


def test_media_mentions_and_adf_fallback_are_dropped():
    storage = (
        '<p>Hi <ac:link><ri:user ri:account-id="abc"/></ac:link>'
        '<ac:image><ri:attachment ri:filename="a.png"/></ac:image></p>'
        '<ac:adf-extension><ac:adf-node type="panel"><ac:adf-content><p>Panel text</p>'
        "</ac:adf-content></ac:adf-node><ac:adf-fallback><p>Panel text</p></ac:adf-fallback>"
        "</ac:adf-extension>"
    )
    assert clean(storage) == "Hi\n\nPanel text"


def test_repeated_blocks_are_deduplicated_but_headings_are_not():
    para = "<p>This paragraph is long enough to count as duplicated boilerplate text.</p>"
    storage = f"<h2>Notes</h2>{para}<h2>Notes</h2>{para}<p>ok</p><p>ok</p>"
    assert clean(storage) == (
        "## Notes\n\nThis paragraph is long enough to count as duplicated boilerplate text."
        "\n\n## Notes\n\nok\n\nok"
    )


def test_configured_and_default_boilerplate_is_removed():
    cleaner = StorageFormatCleaner([r"(?i)this page is maintained by .*"])
    storage = "<p>On this page:</p><p>This page is maintained by Platform.</p><p>Keep me.</p>"
    assert cleaner.clean(storage) == "Keep me."


def test_leading_heading_matching_the_title_is_dropped():
    assert clean("<h1>Runbook</h1><p>Body</p>", "Runbook") == "Body"


def test_whitespace_and_unicode_are_normalised():
    storage = "<p>Non\u00a0breaking\u200b and   spaced\n\n\n text \ufb01x</p>"
    assert clean(storage) == "Non breaking and spaced text fix"


def test_empty_and_macro_only_pages_produce_no_text():
    assert clean("") == ""
    assert clean('<ac:structured-macro ac:name="pagetree"/>') == ""
