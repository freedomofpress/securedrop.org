"CSP compatible variations on DRF classes"
from functools import update_wrapper

from csp.decorators import csp_update
from django.utils.decorators import method_decorator
from rest_framework.routers import DefaultRouter, APIRootView

from django.utils.decorators import classonlymethod
from django.views.decorators.csrf import csrf_exempt


CSP_ADDITIONS = {
    'STYLE_SRC': (
        # float: left
        "'sha256-e+Z0n8P0IwqIce2RMye3/p5TaNb2k/QdJT4urKCsrwk='",
        # clear: both
        "'sha256-matwEc6givhWX0+jiSfM1+E5UMk8/UGLdl902bjFBmY='",
    ),
    'SCRIPT_SRC': (
        # CSRF token
        "'sha256-a3wLtSeBIB9qdbDuQxqq0TbF1eJTelphcOjCUwNtUI4='",
        # ajax form
        "'sha256-IYBrMxCTJ62EwagLTIRncEIpWwTmoXcXkqv3KZm/Wik='",
    )
}


csp_cbv_decorator = method_decorator(csp_update(**CSP_ADDITIONS), name='get')


class CSPCompatibleRouter(DefaultRouter):
    APIRootView = csp_cbv_decorator(APIRootView)


class CSPCompatibleViewSetMixin:
    @classonlymethod
    def as_view(cls, actions=None, **initkwargs):
        """
        Because of the way class based views create a closure around the
        instantiated view, we need to totally reimplement `.as_view`,
        and slightly modify the view function that is created and returned.
        """
        # The name and description initkwargs may be explicitly overridden for
        # certain route confiugurations. eg, names of extra actions.
        cls.name = None
        cls.description = None

        # The suffix initkwarg is reserved for displaying the viewset type.
        # This initkwarg should have no effect if the name is provided.
        # eg. 'List' or 'Instance'.
        cls.suffix = None

        # The detail initkwarg is reserved for introspecting the viewset type.
        cls.detail = None

        # Setting a basename allows a view to reverse its action urls. This
        # value is provided by the router through the initkwargs.
        cls.basename = None

        # actions must not be empty
        if not actions:
            raise TypeError("The `actions` argument must be provided when "
                            "calling `.as_view()` on a ViewSet. For example "
                            "`.as_view({'get': 'list'})`")

        # sanitize keyword arguments
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("You tried to pass in the %s method name as a "
                                "keyword argument to %s(). Don't do that."
                                % (key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r" % (
                    cls.__name__, key))

        # name and suffix are mutually exclusive
        if 'name' in initkwargs and 'suffix' in initkwargs:
            raise TypeError("%s() received both `name` and `suffix`, which are "
                            "mutually exclusive arguments." % (cls.__name__))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            # We also store the mapping of request methods to actions,
            # so that we can later set the action attribute.
            # eg. `self.action = 'list'` on an incoming GET request.
            self.action_map = actions

            # Bind methods to actions
            # This is the bit that's different to a standard view
            for method, action in actions.items():
                handler = getattr(self, action)
                setattr(self, method, handler)

            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get

            self.request = request
            self.args = args
            self.kwargs = kwargs

            # And continue as usual
            return self.dispatch(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())

        # We need to set these on the view function, so that breadcrumb
        # generation can pick out these bits of information from a
        # resolved URL.
        view.cls = cls
        view.initkwargs = initkwargs
        view.actions = actions
        return csp_update(**CSP_ADDITIONS)(csrf_exempt(view))
