#!/bin/bash

# conx Debian Package Builder
# Advanced build script with multiple commands

set -e  # Exit on any error

VERSION="1.0-1"
PACKAGE_NAME="conx"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Show usage information
show_usage() {
    cat << EOF
Usage: ./build.sh [COMMAND]

Commands:
    build       Build the Debian package (default)
    clean       Clean build artifacts
    install     Build and install the package
    uninstall   Uninstall the package
    test        Test the installed package
    rebuild     Clean, then build
    help        Show this help message

Examples:
    ./build.sh              # Build the package
    ./build.sh clean        # Clean build artifacts
    ./build.sh rebuild      # Clean and build
    ./build.sh install      # Build and install

EOF
}

# Check if we're in the right directory
check_directory() {
    if [ ! -f "setup.py" ]; then
        print_error "setup.py not found!"
        print_error "Make sure you're running this from the ${PACKAGE_NAME}-${VERSION%%-*} directory"
        exit 1
    fi

    if [ ! -d "debian" ]; then
        print_error "debian/ directory not found!"
        exit 1
    fi
}

# Clean build artifacts
clean_build() {
    print_info "Cleaning build artifacts..."
    
    # Remove debian build files
    rm -rf debian/${PACKAGE_NAME} 
    rm -rf debian/.debhelper 
    rm -rf debian/debhelper-build-stamp
    rm -f debian/files
    rm -rf debian/tmp
    
    # Remove Python build artifacts
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info
    rm -rf src/*.egg-info
    
    # Remove compiled Python files
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove .deb files in current directory
    rm -f ./${PACKAGE_NAME}_*.deb
    
    # Remove .deb files and build logs in parent directory
    rm -f ../${PACKAGE_NAME}_*.deb 
    rm -f ../${PACKAGE_NAME}_*.build 
    rm -f ../${PACKAGE_NAME}_*.buildinfo 
    rm -f ../${PACKAGE_NAME}_*.changes
    rm -f ../${PACKAGE_NAME}_*.tar.xz
    rm -f ../${PACKAGE_NAME}_*.dsc
    
    # Remove debian/compat if it exists
    if [ -f "debian/compat" ]; then
        print_warning "Removing debian/compat (using debhelper-compat in control instead)"
        rm debian/compat
    fi
    
    print_success "Clean complete!"
}

# Build the package
build_package() {
    print_info "Building ${PACKAGE_NAME} Debian package..."
    
    # Remove debian/compat if it exists
    if [ -f "debian/compat" ]; then
        print_warning "Removing debian/compat to avoid conflicts"
        rm debian/compat
    fi

    # Clean any leftover build artifacts
    if [ -d ".pybuild" ]; then
        print_warning "Cleaning .pybuild directory"
        rm -rf .pybuild
    fi

    if [ -d "conx.egg-info" ]; then
        print_warning "Cleaning egg-info directory"
        rm -rf conx.egg-info
    fi
    
    # Build the package
    dpkg-buildpackage -us -uc
    
    # Move .deb file to current directory
    DEB_FILE=$(ls -t ../${PACKAGE_NAME}_*.deb 2>/dev/null | head -n1)
    if [ -n "$DEB_FILE" ]; then
        print_info "Moving .deb file to current directory..."
        mv "$DEB_FILE" .
        DEB_FILENAME=$(basename "$DEB_FILE")
        print_success "Moved to: ./${DEB_FILENAME}"
    fi

    if [ -d ".pybuild" ]; then
        print_warning "Cleaning .pybuild directory"
        rm -rf .pybuild
    fi

    if [ -d "conx.egg-info" ]; then
        print_warning "Cleaning egg-info directory"
        rm -rf conx.egg-info
    fi
    
    echo ""
    print_success "Build complete!"
    echo ""
    print_info "Package location:"
    ls -lh ./${PACKAGE_NAME}_*.deb 2>/dev/null || print_error "No .deb file found"
    echo ""
}

# Install the package
install_package() {
    # Check current directory first, then parent
    DEB_FILE=$(ls -t ./${PACKAGE_NAME}_*.deb 2>/dev/null | head -n1)
    
    if [ -z "$DEB_FILE" ]; then
        DEB_FILE=$(ls -t ../${PACKAGE_NAME}_*.deb 2>/dev/null | head -n1)
    fi
    
    if [ -z "$DEB_FILE" ]; then
        print_warning "No .deb file found, building first..."
        build_package
        DEB_FILE=$(ls -t ./${PACKAGE_NAME}_*.deb 2>/dev/null | head -n1)
    fi
    
    if [ -z "$DEB_FILE" ]; then
        print_error "Failed to find or build .deb file"
        exit 1
    fi
    
    print_info "Installing ${DEB_FILE}..."
    sudo apt install -y "$DEB_FILE"
    print_success "Installation complete!"
}

# Uninstall the package
uninstall_package() {
    print_info "Uninstalling ${PACKAGE_NAME}..."
    
    if dpkg -l | grep -q "^ii.*${PACKAGE_NAME}"; then
        sudo apt remove -y ${PACKAGE_NAME}
        print_success "Uninstall complete!"
    else
        print_warning "${PACKAGE_NAME} is not installed"
    fi
}

# Test the installed package
test_package() {
    print_info "Testing ${PACKAGE_NAME}..."
    
    if ! command -v ${PACKAGE_NAME} &> /dev/null; then
        print_error "${PACKAGE_NAME} command not found"
        print_error "Make sure the package is installed first"
        exit 1
    fi
    
    print_info "Running: ${PACKAGE_NAME}"
    echo "---"
    ${PACKAGE_NAME}
    echo "---"
    print_success "Test complete!"
}

# Main script logic
main() {
    COMMAND=${1:-build}
    
    case "$COMMAND" in
        build)
            check_directory
            build_package
            ;;
        clean)
            check_directory
            clean_build
            ;;
        install)
            check_directory
            install_package
            ;;
        uninstall)
            uninstall_package
            ;;
        test)
            test_package
            ;;
        rebuild)
            check_directory
            clean_build
            echo ""
            build_package
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

main "$@"