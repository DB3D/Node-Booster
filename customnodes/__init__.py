# SPDX-FileCopyrightText: 2025 BD3D DIGITAL DESIGN (Dorian B.)
#
# SPDX-License-Identifier: GPL-2.0-or-later


from .sockets.custom_sockets import (
        NODEBOOSTER_SK_Interpolation,
        NODEBOOSTER_ND_CustomSocketUtility,
        )
from . camerainfo import (
        NODEBOOSTER_NG_GN_CameraInfo,
        NODEBOOSTER_NG_SH_CameraInfo,
        NODEBOOSTER_NG_CP_CameraInfo,
        )
from . lightinfo import (
        NODEBOOSTER_NG_GN_LightInfo,
        NODEBOOSTER_NG_SH_LightInfo,
        NODEBOOSTER_NG_CP_LightInfo,
        )
from . sceneinfo import (
        NODEBOOSTER_NG_GN_SceneInfo,
        NODEBOOSTER_NG_SH_SceneInfo,
        NODEBOOSTER_NG_CP_SceneInfo,
        )
from . renderinfo import (
        NODEBOOSTER_NG_GN_RenderInfo,
        NODEBOOSTER_NG_SH_RenderInfo,
        NODEBOOSTER_NG_CP_RenderInfo,
        )
from .rnainfo import (
        NODEBOOSTER_NG_GN_RNAInfo,
        NODEBOOSTER_NG_SH_RNAInfo,
        NODEBOOSTER_NG_CP_RNAInfo,
        )
from . isrenderedview import (
        NODEBOOSTER_NG_GN_IsRenderedView,
        )
from . sequencervolume import (
        NODEBOOSTER_NG_GN_SequencerSound,
        NODEBOOSTER_NG_SH_SequencerSound,
        NODEBOOSTER_NG_CP_SequencerSound,
        )
from . mathexpression import (
        NODEBOOSTER_NG_GN_MathExpression,
        NODEBOOSTER_NG_SH_MathExpression,
        NODEBOOSTER_NG_CP_MathExpression,
        )
from . pyexpression import (
        NODEBOOSTER_NG_GN_PyExpression,
        NODEBOOSTER_NG_SH_PyExpression,
        NODEBOOSTER_NG_CP_PyExpression,
        )
from . pynexscript import (
        NODEBOOSTER_NG_GN_PyNexScript,
        NODEBOOSTER_NG_SH_PyNexScript,
        NODEBOOSTER_NG_CP_PyNexScript,
        )
from . keyboardinput import (
        NODEBOOSTER_NG_GN_KeyboardAndMouse,
        NODEBOOSTER_NG_SH_KeyboardAndMouse,
        NODEBOOSTER_NG_CP_KeyboardAndMouse,
        )
from . controllerinput import (
        NODEBOOSTER_NG_GN_XboxPadInput,
        NODEBOOSTER_NG_SH_XboxPadInput,
        NODEBOOSTER_NG_CP_XboxPadInput,
        )
from . objectvelocity import (
        NODEBOOSTER_NG_GN_ObjectVelocity,
        NODEBOOSTER_NG_SH_ObjectVelocity,
        NODEBOOSTER_NG_CP_ObjectVelocity,
        )
from . interpolation.interpolationinput import (
        NODEBOOSTER_OT_interpolation_input_update,
        NODEBOOSTER_NG_GN_InterpolationInput,
        NODEBOOSTER_NG_SH_InterpolationInput,
        NODEBOOSTER_NG_CP_InterpolationInput,
        )
from . interpolation.interpolationmap import (
        NODEBOOSTER_NG_GN_InterpolationMap,
        NODEBOOSTER_NG_SH_InterpolationMap,
        NODEBOOSTER_NG_CP_InterpolationMap,
        )
from . interpolation.interpolationremap import (
        NODEBOOSTER_NG_GN_InterpolationRemap,
        NODEBOOSTER_NG_SH_InterpolationRemap,
        NODEBOOSTER_NG_CP_InterpolationRemap,
        )
from .interpolation.spline2dpreview import (
        NODEBOOSTER_PT_2DCurvePreviewOptions,
        NODEBOOSTER_ND_2DCurvePreview,
        )
from . interpolation.interpolationloop import (
        NODEBOOSTER_ND_InterpolationLoop,
        )
from . interpolation.spline2dinput import (
        NODEBOOSTER_ND_2DCurveInput,
        )
from . interpolation.spline2dsubd import (
        NODEBOOSTER_ND_2DCurveSubdiv,
        )
from . interpolation.spline2dextend import (
        NODEBOOSTER_ND_2DCurveExtend,
        )
from . interpolation.spline2dmix import (
        NODEBOOSTER_ND_2DCurvesMix,
        )
from . interpolation.spline2dmonotonic import (
        NODEBOOSTER_ND_EnsureMonotonicity,
        )
from . colorpalette import (
        NODEBOOSTER_NG_GN_ColorPalette,
        NODEBOOSTER_NG_SH_ColorPalette,
        NODEBOOSTER_NG_CP_ColorPalette,
        )

# For menus, in order of appearance
# NOTE Redudancy. Perhaps menus.py could be refactored to use the _GN_, _SH_, _CP_ notations.
# perhaps we could make use of the poll classmethod to avoid rendundancy.

GN_CustomNodes = (
        ('Inputs',(
            NODEBOOSTER_NG_GN_RNAInfo,
            NODEBOOSTER_NG_GN_LightInfo,
            NODEBOOSTER_NG_GN_SceneInfo,
            NODEBOOSTER_NG_GN_RenderInfo,
            NODEBOOSTER_NG_GN_CameraInfo,
            None, #separator
            NODEBOOSTER_NG_GN_ColorPalette,
            NODEBOOSTER_NG_GN_ObjectVelocity,
            NODEBOOSTER_NG_GN_IsRenderedView, #this one doesn't make sense in other editors.
            NODEBOOSTER_NG_GN_SequencerSound,
            None, #separator
            NODEBOOSTER_NG_GN_KeyboardAndMouse,
            NODEBOOSTER_NG_GN_XboxPadInput,
            ),
        ),
        ('Expressions',(
            NODEBOOSTER_NG_GN_MathExpression,
            NODEBOOSTER_NG_GN_PyExpression,
            NODEBOOSTER_NG_GN_PyNexScript,
            ),
        ),
        ('Interpolation',(
            NODEBOOSTER_NG_GN_InterpolationInput,
            NODEBOOSTER_NG_GN_InterpolationMap,
            NODEBOOSTER_NG_GN_InterpolationRemap,
            NODEBOOSTER_ND_InterpolationLoop,
            None, #separator
            NODEBOOSTER_ND_2DCurvePreview,
            NODEBOOSTER_ND_2DCurveInput,
            NODEBOOSTER_ND_2DCurveExtend,
            NODEBOOSTER_ND_2DCurveSubdiv,
            NODEBOOSTER_ND_2DCurvesMix,
            NODEBOOSTER_ND_EnsureMonotonicity,
            # NODEBOOSTER_ND_CustomSocketUtility, #dev utility. for creating ng with custom sockets manually.
            ),
        ),
    )
SH_CustomNodes = (
        ('Inputs',(
            NODEBOOSTER_NG_SH_RNAInfo,
            NODEBOOSTER_NG_SH_LightInfo,
            NODEBOOSTER_NG_SH_SceneInfo,
            NODEBOOSTER_NG_SH_RenderInfo,
            NODEBOOSTER_NG_SH_CameraInfo,
            None, #separator
            NODEBOOSTER_NG_SH_ColorPalette,
            NODEBOOSTER_NG_SH_ObjectVelocity,
            NODEBOOSTER_NG_SH_SequencerSound,
            None, #separator
            NODEBOOSTER_NG_SH_KeyboardAndMouse,
            NODEBOOSTER_NG_SH_XboxPadInput,
            ),
        ),
        ('Expressions',(
            NODEBOOSTER_NG_SH_MathExpression,
            NODEBOOSTER_NG_SH_PyExpression,
            NODEBOOSTER_NG_SH_PyNexScript,
            ),
        ),
        ('Interpolation',(
            NODEBOOSTER_NG_SH_InterpolationInput,
            NODEBOOSTER_NG_SH_InterpolationMap,
            NODEBOOSTER_NG_SH_InterpolationRemap,
            NODEBOOSTER_ND_InterpolationLoop,
            None, #separator
            NODEBOOSTER_ND_2DCurvePreview,
            NODEBOOSTER_ND_2DCurveInput,
            NODEBOOSTER_ND_2DCurveExtend,
            NODEBOOSTER_ND_2DCurveSubdiv,
            NODEBOOSTER_ND_2DCurvesMix,
            NODEBOOSTER_ND_EnsureMonotonicity,
            # NODEBOOSTER_ND_CustomSocketUtility, #dev utility. for creating ng with custom sockets manually.
            ),
        ), 
    )
CP_CustomNodes = (
        ('Inputs',(
            NODEBOOSTER_NG_CP_RNAInfo,
            NODEBOOSTER_NG_CP_LightInfo,
            NODEBOOSTER_NG_CP_SceneInfo,
            NODEBOOSTER_NG_CP_RenderInfo,
            NODEBOOSTER_NG_CP_CameraInfo,
            None, #separator
            NODEBOOSTER_NG_CP_ObjectVelocity,
            NODEBOOSTER_NG_CP_SequencerSound,
            None, #separator
            NODEBOOSTER_NG_CP_KeyboardAndMouse,
            NODEBOOSTER_NG_CP_XboxPadInput,
            ),
        ),
        ('Expressions',(
            NODEBOOSTER_NG_CP_MathExpression,
            NODEBOOSTER_NG_CP_PyExpression,
            NODEBOOSTER_NG_CP_PyNexScript,
            ),
        ),
        ('Interpolation',(
            NODEBOOSTER_NG_CP_InterpolationInput,
            NODEBOOSTER_NG_CP_InterpolationMap,
            NODEBOOSTER_NG_CP_InterpolationRemap,
            NODEBOOSTER_ND_InterpolationLoop,
            None, #separator
            NODEBOOSTER_ND_2DCurvePreview,
            NODEBOOSTER_ND_2DCurveInput,
            NODEBOOSTER_ND_2DCurveExtend,
            NODEBOOSTER_ND_2DCurveSubdiv,
            NODEBOOSTER_ND_2DCurvesMix,
            NODEBOOSTER_ND_EnsureMonotonicity,
            # NODEBOOSTER_ND_CustomSocketUtility, #dev utility. for creating ng with custom sockets manually.
            ),
        ), 
    )

# for registration
classes = (
    NODEBOOSTER_SK_Interpolation,
    NODEBOOSTER_ND_CustomSocketUtility,
    NODEBOOSTER_NG_GN_CameraInfo,
    NODEBOOSTER_NG_SH_CameraInfo,
    NODEBOOSTER_NG_CP_CameraInfo,
    NODEBOOSTER_NG_GN_LightInfo,
    NODEBOOSTER_NG_SH_LightInfo,
    NODEBOOSTER_NG_CP_LightInfo,
    NODEBOOSTER_NG_GN_SceneInfo,
    NODEBOOSTER_NG_SH_SceneInfo,
    NODEBOOSTER_NG_CP_SceneInfo,
    NODEBOOSTER_NG_GN_RenderInfo,
    NODEBOOSTER_NG_SH_RenderInfo,
    NODEBOOSTER_NG_CP_RenderInfo,
    NODEBOOSTER_NG_GN_RNAInfo,
    NODEBOOSTER_NG_SH_RNAInfo,
    NODEBOOSTER_NG_CP_RNAInfo,
    NODEBOOSTER_NG_GN_IsRenderedView,
    NODEBOOSTER_NG_GN_SequencerSound,
    NODEBOOSTER_NG_SH_SequencerSound,
    NODEBOOSTER_NG_CP_SequencerSound,
    NODEBOOSTER_NG_GN_MathExpression,
    NODEBOOSTER_NG_SH_MathExpression,
    NODEBOOSTER_NG_CP_MathExpression,
    NODEBOOSTER_NG_GN_PyExpression,
    NODEBOOSTER_NG_SH_PyExpression,
    NODEBOOSTER_NG_CP_PyExpression,
    NODEBOOSTER_NG_GN_PyNexScript,
    NODEBOOSTER_NG_SH_PyNexScript,
    NODEBOOSTER_NG_CP_PyNexScript,
    NODEBOOSTER_NG_GN_KeyboardAndMouse,
    NODEBOOSTER_NG_SH_KeyboardAndMouse,
    NODEBOOSTER_NG_CP_KeyboardAndMouse,
    NODEBOOSTER_NG_GN_XboxPadInput,
    NODEBOOSTER_NG_SH_XboxPadInput,
    NODEBOOSTER_NG_CP_XboxPadInput,
    NODEBOOSTER_NG_GN_ObjectVelocity,
    NODEBOOSTER_NG_SH_ObjectVelocity,
    NODEBOOSTER_NG_CP_ObjectVelocity,
    NODEBOOSTER_NG_GN_InterpolationInput,
    NODEBOOSTER_NG_SH_InterpolationInput,
    NODEBOOSTER_NG_CP_InterpolationInput,
    NODEBOOSTER_NG_GN_InterpolationMap,
    NODEBOOSTER_NG_SH_InterpolationMap,
    NODEBOOSTER_NG_CP_InterpolationMap,
    NODEBOOSTER_NG_GN_InterpolationRemap,
    NODEBOOSTER_NG_SH_InterpolationRemap,
    NODEBOOSTER_NG_CP_InterpolationRemap,
    NODEBOOSTER_ND_2DCurvePreview,
    NODEBOOSTER_PT_2DCurvePreviewOptions,
    NODEBOOSTER_OT_interpolation_input_update,
    NODEBOOSTER_ND_2DCurveInput,
    NODEBOOSTER_ND_2DCurveSubdiv,
    NODEBOOSTER_ND_2DCurveExtend,
    NODEBOOSTER_ND_2DCurvesMix,
    NODEBOOSTER_ND_EnsureMonotonicity,
    NODEBOOSTER_ND_InterpolationLoop,
    NODEBOOSTER_NG_GN_ColorPalette,
    NODEBOOSTER_NG_SH_ColorPalette,
    NODEBOOSTER_NG_CP_ColorPalette,
    )

#for utility. handlers.py module will use this list.
allcustomnodes = tuple(cls for cls in classes if
                  (('_NG_' in cls.__name__) or
                   ('_ND_' in cls.__name__)) )