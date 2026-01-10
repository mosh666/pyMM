# Internationalization (i18n) Strategy for pyMediaManager Documentation

## Overview

This document outlines the internationalization strategy for pyMediaManager
documentation, designed to support multi-language documentation with a focus on
community-driven translations.

## Primary Target Language

**German (Deutsch)** - Primary translation target for the following reasons:

- Strong European open-source community
- Significant user base in German-speaking countries (Germany, Austria, Switzerland)
- Active contributor base for translation maintenance
- Natural second language for expanding international reach

## Translation Infrastructure

### Technology Stack

- **Sphinx i18n**: Built-in internationalization support using `sphinx.ext.intl`
- **sphinx-intl**: Command-line tool for managing translations
- **gettext**: Standard GNU translation system (.po/.pot files)
- **Transifex/Weblate** (future): Optional web-based translation platform integration

### Directory Structure

```text
docs/
├── locales/          # Translation files
│   ├── de/           # German translations
│   │   └── LC_MESSAGES/
│   │       ├── index.po
│   │       ├── user-guide.po
│   │       ├── architecture.po
│   │       └── ...
│   ├── fr/           # Future: French
│   ├── es/           # Future: Spanish
│   └── ...
├── _build/           # Built documentation
│   ├── html/         # English (default)
│   ├── html-de/      # German build
│   └── ...
└── *.md              # Source documentation (English)
```

## Translation Workflow

### For Contributors

#### 1. Extract Translatable Strings

```bash
# Generate .pot (Portable Object Template) files from source
just docs-gettext

# or manually:
sphinx-build -b gettext docs docs/_build/gettext
```

#### 2. Update Translation Files

```bash
# Update .po files for German locale
just docs-translate

# or manually:
sphinx-intl update -p docs/_build/gettext -l de
```

#### 3. Translate Content

Edit `.po` files in `docs/locales/de/LC_MESSAGES/`:

```po
# Example translation entry
#: ../../user-guide.md:23
msgid "Installation"
msgstr "Installation"

#: ../../user-guide.md:25
msgid "To install pyMediaManager, follow these steps:"
msgstr "Um pyMediaManager zu installieren, folgen Sie diesen Schritten:"
```

#### 4. Build Translated Documentation

```bash
# Build German documentation
just docs-build-de

# or manually:
sphinx-build -b html -D language=de docs docs/_build/html-de
```

### For Maintainers

#### Review Translation Quality

- Verify technical terminology consistency
- Check formatting and markup preservation
- Ensure code examples remain unchanged
- Test rendered output in target language

#### Merge Translation PRs

- Translations submitted via pull requests
- Review by native speakers when possible
- Automated checks for .po file validity
- CI builds translated documentation to verify

## Community-Driven Translation Model

### Contribution Guidelines

1. **No Technical Expertise Required**: Translators don't need programming knowledge
2. **Clear Attribution**: Translators credited in documentation footer
3. **Incremental Translation**: Partial translations acceptable and encouraged
4. **Quality Over Speed**: Prefer accurate translations over quick completion

### Translation Priorities

**Priority 1 - High Impact** (Translate First):

- README.md
- docs/index.md
- docs/user-guide.md
- docs/troubleshooting.md

**Priority 2 - User-Facing**:

- docs/plugin-catalog.md
- docs/migration-guide.md
- docs/platform-directories.md

**Priority 3 - Developer Documentation**:

- docs/plugin-development.md
- docs/architecture.md
- docs/api-reference.md

**Priority 4 - Advanced Topics**:

- docs/docker-ci-testing.md
- docs/linux-udev-installer.md

### Translation Terminology

Maintain a **glossary** for consistent technical term translation:

| English | Deutsch | Notes |
| ------- | ------- | ----- |
| Project | Projekt | |
| Plugin | Plugin | Keep as-is (common in German) |
| Portable Mode | Portabler Modus | |
| Storage | Speicher | |
| Tool | Werkzeug | |
| Template | Vorlage | |
| Configuration | Konfiguration | |
| Fluent UI | Fluent UI | Keep as-is (product name) |

## Future Language Expansion

### Criteria for Adding Languages

1. **Active Community**: At least 2-3 committed translators
2. **Maintenance Plan**: Long-term maintenance commitment
3. **User Demand**: Documented user requests or analytics data
4. **Resource Availability**: Sufficient CI/hosting resources

### Potential Future Languages

- **French (Français)**: Large European/Canadian user base
- **Spanish (Español)**: Global reach (Spain + Latin America)
- **Italian (Italiano)**: European community
- **Portuguese (Português)**: Brazilian open-source community
- **Japanese (日本語)**: Asian market interest
- **Chinese (中文)**: Largest potential user base

## Translation Management Tools

### Current: Manual Git Workflow

- Translations in Git repository
- Pull request-based contributions
- CI automated testing

### Future: Web Platform Integration

**Option 1: Weblate** (Open Source)

- Self-hosted or cloud-hosted
- Git integration
- Translation memory
- Community features

**Option 2: Transifex** (Commercial/Free for OSS)

- Popular in open-source
- Good tooling
- Active community

**Option 3: Crowdin** (Commercial/Free for OSS)

- Strong GitHub integration
- Real-time collaboration
- In-context translation

## Translation Quality Assurance

### Automated Checks

- **Syntax validation**: `msgfmt --check` for .po files
- **Coverage tracking**: Monitor translation completion percentage
- **Build verification**: CI builds all language versions
- **Link validation**: Ensure cross-references work in translations

### Manual Review

- Native speaker review before major releases
- Community feedback mechanism
- Regular translation audits
- Update notifications for source changes

## Version Management

### Handling Documentation Updates

1. **Source changes tracked**: Git history shows English updates
2. **Translation outdated markers**: sphinx-intl marks outdated translations
3. **Fuzzy matching**: Automatic matching for minor changes
4. **Translator notifications**: GitHub issues/PRs for translation updates

### Release Coordination

- Translations updated before major releases
- Feature documentation translated with feature releases
- Hotfix documentation in English first, translations follow

## Contributor Recognition

### Attribution

- **Translation credits**: Added to documentation footer
- **Contributors page**: Dedicated translators section
- **Commit history**: Preserves individual contributions
- **Release notes**: Mention translation updates

### Community Building

- **Translation team**: Create dedicated GitHub team
- **Communication channels**: Discord/Matrix channel for translators
- **Translation sprints**: Organized events for focused translation
- **Documentation**: This strategy document + CONTRIBUTING.md guidelines

## Technical Implementation Notes

### Configuration

In `docs/conf.py`:

```python
# i18n configuration
locale_dirs = ["locales/"]
gettext_compact = False
language = "en"  # Default language
```

### Build System Integration

In `justfile`:

```justfile
# Extract translatable strings
docs-gettext:
    sphinx-build -b gettext docs docs/_build/gettext

# Update translation files
docs-translate:
    sphinx-intl update -p docs/_build/gettext -l de

# Build German documentation
docs-build-de:
    sphinx-build -b html -D language=de docs docs/_build/html-de
```

### GitHub Actions

Future CI integration:

```yaml
- name: Build German Documentation
  run: |
    sphinx-build -b html -D language=de docs docs/_build/html-de
- name: Validate .po files
  run: |
    find docs/locales -name "*.po" -exec msgfmt --check {} \;
```

## Resources

### Documentation

- [Sphinx Internationalization](https://www.sphinx-doc.org/en/master/usage/advanced/intl.html)
- [sphinx-intl Documentation](https://sphinx-intl.readthedocs.io/)
- [GNU gettext Manual](https://www.gnu.org/software/gettext/manual/)

### Tools

- `sphinx-intl`: Translation file management
- `poedit`: GUI editor for .po files
- `msgfmt`: .po file validation
- `translate-toolkit`: Advanced translation utilities

## Contact

For questions about translation:

- **GitHub Discussions**: Translation-related topics
- **Issues**: Translation bugs or suggestions
- **Contributing Guide**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Last Updated**: January 10, 2026
**Status**: Active - Seeking German translators
**Next Review**: Upon completion of first German translation milestone
