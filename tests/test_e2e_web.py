"""
E2E 测试 - Memora Connect Web 界面
使用 Playwright 进行端到端测试
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def browser_context_args():
    """浏览器上下文配置"""
    return {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


def test_page_loads(page: Page):
    """测试页面加载"""
    page.goto("http://localhost:8352")
    expect(page).to_have_title("Memora Connect")


def test_header_visible(page: Page):
    """测试头部区域可见"""
    page.goto("http://localhost:8352")
    header = page.locator(".app-header")
    expect(header).to_be_visible()


def test_concept_list_visible(page: Page):
    """测试概念列表可见"""
    page.goto("http://localhost:8352")
    page.wait_for_selector("#conceptList .list-item", timeout=5000)
    concepts = page.locator("#conceptList .list-item")
    expect(concepts.first).to_be_visible()


def test_memory_tab_click(page: Page):
    """测试点击记忆标签"""
    page.goto("http://localhost:8352")
    page.wait_for_selector('[data-tab="memories"]', timeout=5000)
    page.click('[data-tab="memories"]')
    memory_tab = page.locator("#tab-memories")
    expect(memory_tab).to_be_visible()


def test_impression_tab_click(page: Page):
    """测试点击印象标签"""
    page.goto("http://localhost:8352")
    page.wait_for_selector('[data-tab="impressions"]', timeout=5000)
    page.click('[data-tab="impressions"]')
    impression_tab = page.locator("#tab-impressions")
    expect(impression_tab).to_be_visible()


def test_search_input_visible(page: Page):
    """测试搜索框可见"""
    page.goto("http://localhost:8352")
    search = page.locator("#globalSearch")
    expect(search).to_be_visible()


def test_graph_visible(page: Page):
    """测试图谱区域可见"""
    page.goto("http://localhost:8352")
    page.wait_for_selector("#graph", timeout=5000)
    graph = page.locator("#graph")
    expect(graph).to_be_visible()


def test_group_select_visible(page: Page):
    """测试分组选择器可见"""
    page.goto("http://localhost:8352")
    group_select = page.locator("#groupSelect")
    expect(group_select).to_be_visible()
