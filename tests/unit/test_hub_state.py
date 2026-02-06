"""
Unit tests for Hub Just-In-Time Awareness (JIT) feature.

Tests the top-level feature requirements from policy-hub-jit-awareness lug:
- Auto-expiry and curation of quota entries
- Push notification activation
- Non-expiring data support
- Hub state initialization and updates
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from wai.hub_state import (
    get_hub_state,
    initialize_hub_state,
    update_hub_state,
    update_tool_quota,
    push_notification,
    clear_notification,
    format_hub_context_for_agent,
    _cleanup_expired_quotas,
)


@pytest.fixture
def mock_hub(tmp_path: Path) -> Path:
    """Create a temporary hub directory."""
    hub_path = tmp_path / "test-hub"
    hub_path.mkdir()
    return hub_path


def test_initialize_hub_state_creates_valid_structure(mock_hub: Path):
    """Verify hub state initialization creates proper schema."""
    state = initialize_hub_state(mock_hub)
    
    assert 'tool_quotas' in state
    assert 'ide_preferences' in state
    assert 'tool_recommendations' in state
    assert 'pending_actions' in state
    assert 'notifications' in state
    assert 'last_updated' in state
    
    # Verify schema documentation exists
    assert '_schema' in state['tool_quotas']
    assert '_note' in state['ide_preferences']
    assert '_note' in state['notifications']


def test_update_tool_quota_with_expiry(mock_hub: Path):
    """Test quota update with expiration timestamp."""
    initialize_hub_state(mock_hub)
    
    future_time = (datetime.now() + timedelta(hours=1)).isoformat()
    
    success = update_tool_quota(
        tool_name='amp',
        used=95,
        limit=100,
        unit='requests',
        expires_at=future_time,
        message='Add credits or wait',
        hub_path=mock_hub,
        notify_spokes=False  # Disable for unit test
    )
    
    assert success
    
    state = get_hub_state(mock_hub)
    assert 'amp' in state['tool_quotas']
    assert state['tool_quotas']['amp']['used'] == 95
    assert state['tool_quotas']['amp']['limit'] == 100
    assert state['tool_quotas']['amp']['unit'] == 'requests'
    assert state['tool_quotas']['amp']['expires_at'] == future_time
    assert state['tool_quotas']['amp']['message'] == 'Add credits or wait'


def test_update_tool_quota_without_expiry(mock_hub: Path):
    """Test quota update without expiration (persists indefinitely)."""
    initialize_hub_state(mock_hub)
    
    success = update_tool_quota(
        tool_name='custom_tool',
        used=10,
        limit=50,
        unit='credits',
        expires_at=None,  # No expiry
        hub_path=mock_hub,
        notify_spokes=False
    )
    
    assert success
    
    state = get_hub_state(mock_hub)
    assert 'custom_tool' in state['tool_quotas']
    assert state['tool_quotas']['custom_tool']['expires_at'] is None


def test_cleanup_expired_quotas_removes_past_entries(mock_hub: Path):
    """Verify expired quotas are automatically cleaned up."""
    state = initialize_hub_state(mock_hub)
    
    # Add expired quota
    past_time = (datetime.now() - timedelta(hours=1)).isoformat()
    state['tool_quotas']['expired_tool'] = {
        'used': 50,
        'limit': 100,
        'expires_at': past_time
    }
    
    # Add future quota
    future_time = (datetime.now() + timedelta(hours=1)).isoformat()
    state['tool_quotas']['active_tool'] = {
        'used': 25,
        'limit': 100,
        'expires_at': future_time
    }
    
    # Add non-expiring quota
    state['tool_quotas']['persistent_tool'] = {
        'used': 10,
        'limit': 50,
        'expires_at': None
    }
    
    # Run cleanup
    _cleanup_expired_quotas(state, mock_hub)
    
    # Verify expired removed, others remain
    assert 'expired_tool' not in state['tool_quotas']
    assert 'active_tool' in state['tool_quotas']
    assert 'persistent_tool' in state['tool_quotas']


def test_cleanup_expired_quotas_preserves_schema_entries(mock_hub: Path):
    """Ensure cleanup doesn't remove schema/example entries."""
    state = initialize_hub_state(mock_hub)
    
    # Add expired quota
    past_time = (datetime.now() - timedelta(hours=1)).isoformat()
    state['tool_quotas']['expired_tool'] = {
        'used': 50,
        'limit': 100,
        'expires_at': past_time
    }
    
    # Run cleanup
    _cleanup_expired_quotas(state, mock_hub)
    
    # Schema entries should remain
    assert '_schema' in state['tool_quotas']
    assert '_example' in state['tool_quotas']


def test_push_notification_critical_priority(mock_hub: Path):
    """Test critical priority notification push."""
    initialize_hub_state(mock_hub)
    
    push_notification(
        message='Critical quota warning',
        priority='critical',
        hub_path=mock_hub
    )
    
    state = get_hub_state(mock_hub)
    assert len(state['notifications']['pending']) == 1
    
    notif = state['notifications']['pending'][0]
    assert notif['message'] == 'Critical quota warning'
    assert notif['priority'] == 'critical'
    assert 'timestamp' in notif
    assert 'id' in notif


def test_update_tool_quota_triggers_notification_at_90_percent(mock_hub: Path):
    """Verify automatic notification at 90% threshold."""
    initialize_hub_state(mock_hub)
    
    update_tool_quota(
        tool_name='amp',
        used=90,
        limit=100,
        hub_path=mock_hub,
        notify_spokes=True
    )
    
    state = get_hub_state(mock_hub)
    # Should have notification since 90% >= 90% threshold
    assert len(state['notifications']['pending']) >= 1


def test_update_tool_quota_triggers_notification_at_70_percent(mock_hub: Path):
    """Verify automatic notification at 70% threshold."""
    initialize_hub_state(mock_hub)
    
    update_tool_quota(
        tool_name='claude_code',
        used=75,
        limit=100,
        hub_path=mock_hub,
        notify_spokes=True
    )
    
    state = get_hub_state(mock_hub)
    # Should have notification since 75% >= 70% threshold
    assert len(state['notifications']['pending']) >= 1


def test_update_tool_quota_no_notification_below_70_percent(mock_hub: Path):
    """Verify no notification below 70% threshold."""
    initialize_hub_state(mock_hub)
    
    update_tool_quota(
        tool_name='low_usage_tool',
        used=50,
        limit=100,
        hub_path=mock_hub,
        notify_spokes=True
    )
    
    state = get_hub_state(mock_hub)
    # Should have no notifications since 50% < 70%
    assert len(state['notifications']['pending']) == 0


def test_clear_notification_removes_by_id(mock_hub: Path):
    """Test notification clearing by ID."""
    initialize_hub_state(mock_hub)
    
    push_notification('Test notification', 'normal', mock_hub)
    
    state = get_hub_state(mock_hub)
    notif_id = state['notifications']['pending'][0]['id']
    
    clear_notification(notif_id, mock_hub)
    
    state = get_hub_state(mock_hub)
    assert len(state['notifications']['pending']) == 0


def test_format_hub_context_displays_quota_with_percentage(mock_hub: Path):
    """Verify quota display includes usage percentage."""
    initialize_hub_state(mock_hub)
    
    update_tool_quota(
        tool_name='amp',
        used=95,
        limit=100,
        unit='requests',
        hub_path=mock_hub,
        notify_spokes=False
    )
    
    context = format_hub_context_for_agent(mock_hub)
    
    assert context is not None
    assert 'AMP' in context
    assert '95/100' in context
    assert '95%' in context


def test_format_hub_context_shows_critical_icon_at_90_percent(mock_hub: Path):
    """Verify critical icon (🚨) appears at 90%+ usage."""
    initialize_hub_state(mock_hub)
    
    update_tool_quota(
        tool_name='amp',
        used=95,
        limit=100,
        hub_path=mock_hub,
        notify_spokes=False
    )
    
    context = format_hub_context_for_agent(mock_hub)
    
    assert '🚨' in context


def test_format_hub_context_shows_warning_icon_at_70_percent(mock_hub: Path):
    """Verify warning icon (⚠️) appears at 70%+ usage."""
    initialize_hub_state(mock_hub)
    
    update_tool_quota(
        tool_name='claude_code',
        used=75,
        limit=100,
        hub_path=mock_hub,
        notify_spokes=False
    )
    
    context = format_hub_context_for_agent(mock_hub)
    
    assert '⚠️' in context


def test_format_hub_context_shows_time_until_reset(mock_hub: Path):
    """Verify time until reset is displayed."""
    initialize_hub_state(mock_hub)
    
    future_time = (datetime.now() + timedelta(hours=2, minutes=30)).isoformat()
    
    update_tool_quota(
        tool_name='amp',
        used=95,
        limit=100,
        expires_at=future_time,
        hub_path=mock_hub,
        notify_spokes=False
    )
    
    context = format_hub_context_for_agent(mock_hub)
    
    # Should show something like "resets in 2h 30m"
    assert 'resets in' in context
    assert 'h' in context or 'm' in context


def test_format_hub_context_shows_custom_message(mock_hub: Path):
    """Verify custom message is displayed with quota."""
    initialize_hub_state(mock_hub)
    
    update_tool_quota(
        tool_name='amp',
        used=95,
        limit=100,
        message='Add credits or wait until next hour',
        hub_path=mock_hub,
        notify_spokes=False
    )
    
    context = format_hub_context_for_agent(mock_hub)
    
    assert 'Add credits or wait until next hour' in context


def test_format_hub_context_auto_cleanup_on_read(mock_hub: Path):
    """Verify expired quotas are cleaned up when formatting context."""
    state = initialize_hub_state(mock_hub)
    
    # Add expired quota
    past_time = (datetime.now() - timedelta(hours=1)).isoformat()
    state['tool_quotas']['expired_tool'] = {
        'used': 50,
        'limit': 100,
        'expires_at': past_time
    }
    
    # Save state
    state_file = mock_hub / 'hub-state.json'
    state_file.write_text(json.dumps(state, indent=2))
    
    # Format context (should trigger cleanup)
    format_hub_context_for_agent(mock_hub)
    
    # Verify cleanup occurred
    state = get_hub_state(mock_hub)
    assert 'expired_tool' not in state['tool_quotas']


def test_ide_preferences_persist_across_updates(mock_hub: Path):
    """Verify IDE preferences don't expire or get cleaned."""
    state = initialize_hub_state(mock_hub)
    
    original_preferences = state['ide_preferences']['tools'].copy()
    
    # Update other state
    update_tool_quota(
        tool_name='test_tool',
        used=50,
        limit=100,
        hub_path=mock_hub,
        notify_spokes=False
    )
    
    # Verify preferences unchanged
    state = get_hub_state(mock_hub)
    assert state['ide_preferences']['tools'] == original_preferences


def test_notifications_persist_until_cleared(mock_hub: Path):
    """Verify notifications don't auto-expire."""
    initialize_hub_state(mock_hub)
    
    push_notification('Test notification', 'normal', mock_hub)
    
    # Add and cleanup expired quota
    state = get_hub_state(mock_hub)
    past_time = (datetime.now() - timedelta(hours=1)).isoformat()
    state['tool_quotas']['expired_tool'] = {
        'used': 50,
        'limit': 100,
        'expires_at': past_time
    }
    state_file = mock_hub / 'hub-state.json'
    state_file.write_text(json.dumps(state, indent=2))
    
    # Trigger cleanup via format
    format_hub_context_for_agent(mock_hub)
    
    # Notification should still exist
    state = get_hub_state(mock_hub)
    assert len(state['notifications']['pending']) == 1


def test_update_hub_state_deep_merge(mock_hub: Path):
    """Test deep merge functionality for nested updates."""
    initialize_hub_state(mock_hub)
    
    update_hub_state({
        'tool_quotas': {
            'new_tool': {
                'used': 10,
                'limit': 100
            }
        }
    }, mock_hub)
    
    state = get_hub_state(mock_hub)
    
    # New tool should exist
    assert 'new_tool' in state['tool_quotas']
    # Schema entries should still exist
    assert '_schema' in state['tool_quotas']


def test_format_hub_context_returns_none_when_empty(mock_hub: Path):
    """Verify format returns None when no relevant info to display."""
    initialize_hub_state(mock_hub)
    
    context = format_hub_context_for_agent(mock_hub)
    
    # Should return None since no quotas or notifications
    assert context is None
